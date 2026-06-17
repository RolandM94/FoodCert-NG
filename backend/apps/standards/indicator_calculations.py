from decimal import Decimal, InvalidOperation

from apps.forms.models import FormResponse, FormTemplateVersion, ResponseStatus


class IndicatorCalculationError(ValueError):
    pass


FORM_RESPONSE_STATUSES_FOR_CALCULATION = {
    ResponseStatus.SUBMITTED,
    ResponseStatus.REVIEWED,
    ResponseStatus.APPROVED,
}


def schema_question_keys(schema_json):
    keys = set()
    for section in (schema_json or {}).get("sections", []):
        for question in section.get("questions", []):
            key = question.get("key")
            if key:
                keys.add(key)
            for nested in question.get("questions", []) or []:
                nested_key = nested.get("key")
                if nested_key:
                    keys.add(nested_key)
    return keys


class IndicatorFormSourceAdapter:
    @classmethod
    def validate_form_source(cls, source_config):
        if source_config.source_type != "form":
            return []
        if not source_config.source_id:
            return ["Select a form template."]
        version = FormTemplateVersion.objects.filter(template_id=source_config.source_id).order_by("-version_number").first()
        if not version:
            return ["The selected form does not have a schema version."]
        keys = schema_question_keys(version.schema_json)
        required_fields = [source_config.value_field_id, source_config.unicity_field_id]
        for component in [source_config.numerator_config_json, source_config.denominator_config_json]:
            required_fields.extend([
                component.get("value_field_id", ""),
                component.get("unicity_field_id", ""),
            ])
        for rule in (source_config.filter_config_json or {}).get("filters", []):
            required_fields.append(rule.get("field", ""))
        missing = sorted({field for field in required_fields if field and field not in keys})
        return [f"Unknown form field: {field}" for field in missing]

    @classmethod
    def records_for_source(cls, source_config, period=None):
        errors = cls.validate_form_source(source_config)
        if errors:
            raise IndicatorCalculationError(errors[0])
        responses = FormResponse.objects.filter(
            template_id=source_config.source_id,
            status__in=FORM_RESPONSE_STATUSES_FOR_CALCULATION,
        )
        period = period or {}
        start = period.get("period_start")
        end = period.get("period_end")
        if start and end:
            responses = responses.filter(submitted_at__date__gte=start, submitted_at__date__lte=end)

        records = []
        for form_response in responses.select_related("template", "respondent_organization"):
            record = dict(form_response.response_json or {})
            record.update({
                "_response_id": str(form_response.id),
                "_submitted_at": form_response.submitted_at.date().isoformat() if form_response.submitted_at else "",
                "_status": form_response.status,
                "_organization_id": str(form_response.respondent_organization_id or ""),
            })
            records.append(record)
        return records


class IndicatorIndicatorSourceAdapter:
    @classmethod
    def source_indicator_ids(cls, source_config):
        raw_ids = (source_config.filter_config_json or {}).get("source_kpi_ids", (source_config.filter_config_json or {}).get("source_indicator_ids", []))
        if isinstance(raw_ids, str):
            raw_ids = [raw_ids]
        return [str(indicator_id) for indicator_id in raw_ids if indicator_id]

    @classmethod
    def validate_indicator_source(cls, source_config):
        if source_config.source_type != "kpi":
            return []

        from apps.standards.models import MEIndicator, MEIndicatorDataSource

        target_id = str(source_config.indicator_id or getattr(source_config.indicator, "id", ""))
        source_ids = cls.source_indicator_ids(source_config)
        if not source_ids:
            return ["Select at least one source indicator."]
        if source_config.calculation_method not in {"sum", "average", "percentage", "ratio", "formula"}:
            return ["KPI data sources support Sum, Average, Percentage, Ratio, or Formula."]
        if target_id and target_id in source_ids:
            return ["An indicator cannot depend on itself."]

        found_ids = set(str(indicator_id) for indicator_id in MEIndicator.objects.filter(id__in=source_ids).values_list("id", flat=True))
        missing_ids = sorted(set(source_ids) - found_ids)
        if missing_ids:
            return [f"Unknown source indicator: {missing_ids[0]}"]

        graph = {}
        existing_sources = MEIndicatorDataSource.objects.filter(source_type="kpi").exclude(id=getattr(source_config, "id", None))
        for existing_source in existing_sources:
            graph.setdefault(str(existing_source.indicator_id), set()).update(cls.source_indicator_ids(existing_source))
        if target_id:
            graph[target_id] = set(source_ids)

        def reaches_target(indicator_id, visited):
            if indicator_id == target_id:
                return True
            if indicator_id in visited:
                return False
            visited.add(indicator_id)
            return any(reaches_target(next_id, visited) for next_id in graph.get(indicator_id, set()))

        for source_id in source_ids:
            if reaches_target(source_id, set()):
                return ["Circular indicator dependencies are not allowed."]
        return []

    @classmethod
    def records_for_source(cls, source_config, period=None):
        errors = cls.validate_indicator_source(source_config)
        if errors:
            raise IndicatorCalculationError(errors[0])

        from apps.standards.models import IndicatorValueStatus, MEIndicatorValue

        values = MEIndicatorValue.objects.filter(
            indicator_id__in=cls.source_indicator_ids(source_config),
            approval_status=IndicatorValueStatus.APPROVED,
        ).select_related("indicator")

        period = period or {}
        start = period.get("period_start")
        end = period.get("period_end")
        if source_config.period_filter_mode != "all_time" and start and end:
            values = values.filter(period_start__gte=start, period_end__lte=end)

        records = []
        for value in values:
            numeric_value = value.cumulative_value_numeric
            if numeric_value is None:
                numeric_value = value.progress_value_numeric
            records.append({
                "_indicator_id": str(value.indicator_id),
                "_indicator_code": value.indicator.indicator_code,
                "_indicator_name": value.indicator.indicator_name,
                "_value_id": str(value.id),
                "_period_start": value.period_start.isoformat(),
                "_period_end": value.period_end.isoformat(),
                "value": str(numeric_value or Decimal("0")),
            })
        return records


class IndicatorCalculationService:
    @classmethod
    def calculate(cls, source_config, records, period=None, disaggregations=None):
        period = period or {}
        if source_config.source_type == "kpi" and not records:
            records = IndicatorIndicatorSourceAdapter.records_for_source(source_config, period)
        records = cls.apply_period_filter(records or [], source_config.period_filter_mode, source_config.filter_config_json, period)
        records = cls.apply_filters(records, source_config.filter_config_json)
        method = source_config.calculation_method

        if method == "sum":
            value = cls.calculate_sum(source_config, records)
            numerator = value
            denominator = None
        elif method == "count":
            value = Decimal(len(records))
            numerator = value
            denominator = None
        elif method == "unique_count":
            unique_records = cls.apply_unicity(records, source_config.unicity_field_id)
            value = Decimal(len(unique_records))
            numerator = value
            denominator = None
        elif method == "average":
            value = cls.calculate_average(source_config, records)
            numerator = value
            denominator = None
        elif method == "percentage":
            value, numerator, denominator = cls.calculate_percentage(source_config, records)
        elif method == "ratio":
            value, numerator, denominator = cls.calculate_ratio(source_config, records)
        elif method == "formula":
            value, numerator, denominator = cls.calculate_formula(source_config, records)
        else:
            raise IndicatorCalculationError(f"Unsupported calculation method: {method}")

        disaggregated_values = cls.calculate_disaggregations(source_config, records, disaggregations or [])
        return {
            "value": value,
            "numerator": numerator,
            "denominator": denominator,
            "record_count": len(records),
            "disaggregations": disaggregated_values,
            "snapshot": {
                "source_type": source_config.source_type,
                "source_id": source_config.source_id,
                "calculation_method": method,
                "value_field_id": source_config.value_field_id,
                "unicity_field_id": source_config.unicity_field_id,
                "period_filter_mode": source_config.period_filter_mode,
                "source_kpi_ids": IndicatorIndicatorSourceAdapter.source_indicator_ids(source_config) if source_config.source_type == "kpi" else [],
                "period": period,
                "record_count": len(records),
                "disaggregation_count": len(disaggregated_values),
                "numerator": str(numerator) if numerator is not None else None,
                "denominator": str(denominator) if denominator is not None else None,
                "value": str(value),
            },
        }

    @classmethod
    def calculate_disaggregations(cls, source_config, records, disaggregations):
        dimensions = sorted(disaggregations, key=lambda dimension: dimension.level)
        if not dimensions:
            return []
        groups = {}
        for record in records:
            key = tuple(str(record.get(dimension.field_id, "") or "Unspecified") for dimension in dimensions)
            groups.setdefault(key, []).append(record)

        values = []
        for key, group_records in groups.items():
            dimension_values = {
                dimensions[index].field_label: key[index]
                for index in range(len(dimensions))
            }
            if source_config.calculation_method == "average":
                value = cls.calculate_average(source_config, group_records)
            elif source_config.calculation_method == "sum":
                value = cls.calculate_sum(source_config, group_records)
            else:
                value = Decimal(len(group_records))
            values.append({
                "dimension_values_json": dimension_values,
                "value_numeric": value,
            })
        return values

    @classmethod
    def calculate_sum(cls, source_config, records):
        return sum((cls.decimal_value(record.get(source_config.value_field_id)) for record in records), Decimal("0"))

    @classmethod
    def calculate_count(cls, records):
        return Decimal(len(records))

    @classmethod
    def calculate_unique_count(cls, records, unicity_field):
        return Decimal(len(cls.apply_unicity(records, unicity_field)))

    @classmethod
    def calculate_average(cls, source_config, records):
        values = [cls.decimal_value(record.get(source_config.value_field_id)) for record in records if record.get(source_config.value_field_id) not in (None, "")]
        if not values:
            return Decimal("0")
        return sum(values, Decimal("0")) / Decimal(len(values))

    @classmethod
    def calculate_percentage(cls, source_config, records):
        numerator = cls.calculate_component(source_config.numerator_config_json, records)
        denominator = cls.calculate_component(source_config.denominator_config_json, records)
        if denominator == 0:
            raise IndicatorCalculationError("Percentage denominator cannot be zero.")
        return (numerator / denominator) * Decimal("100"), numerator, denominator

    @classmethod
    def calculate_ratio(cls, source_config, records):
        numerator = cls.calculate_component(source_config.numerator_config_json, records)
        denominator = cls.calculate_component(source_config.denominator_config_json, records)
        if denominator == 0:
            raise IndicatorCalculationError("Ratio denominator cannot be zero.")
        return numerator / denominator, numerator, denominator

    @classmethod
    def calculate_formula(cls, source_config, records):
        config = source_config.filter_config_json or {}
        expression = str(config.get("formula_expression") or "").strip()
        if not expression:
            raise IndicatorCalculationError("Formula expression is required.")
        variables = {
            "count": Decimal(len(records)),
            "sum": cls.calculate_sum(source_config, records),
            "average": cls.calculate_average(source_config, records),
        }
        for name, value in (config.get("variables") or {}).items():
            variables[str(name)] = cls.decimal_value(value)
        allowed_names = set(variables)
        for token in expression.replace("+", " ").replace("-", " ").replace("*", " ").replace("/", " ").replace("(", " ").replace(")", " ").split():
            if token.replace(".", "", 1).isdigit():
                continue
            if token not in allowed_names:
                raise IndicatorCalculationError(f"Unknown formula variable: {token}")
        try:
            value = eval(expression, {"__builtins__": {}}, variables)  # noqa: S307 - expression variables are whitelisted above.
        except Exception as exc:
            raise IndicatorCalculationError("Formula could not be evaluated.") from exc
        return cls.decimal_value(value), None, None

    @classmethod
    def calculate_component(cls, config, records):
        config = config or {}
        method = config.get("calculation_method", "sum")
        value_field = config.get("value_field_id", "")
        component_records = cls.apply_filters(records, config)
        component_records = cls.apply_unicity(component_records, config.get("unicity_field_id", ""))
        if method == "sum":
            return sum((cls.decimal_value(record.get(value_field)) for record in component_records), Decimal("0"))
        if method == "average":
            values = [cls.decimal_value(record.get(value_field)) for record in component_records if record.get(value_field) not in (None, "")]
            return sum(values, Decimal("0")) / Decimal(len(values)) if values else Decimal("0")
        if method == "count":
            return Decimal(len(component_records))
        if method == "unique_count":
            return Decimal(len(component_records))
        raise IndicatorCalculationError(f"Unsupported percentage component method: {method}")

    @classmethod
    def apply_filters(cls, records, filter_config):
        filters = (filter_config or {}).get("filters", [])
        if not filters:
            return list(records)
        filtered = list(records)
        for rule in filters:
            field = rule.get("field")
            operator = rule.get("operator", "eq")
            expected = rule.get("value")
            filtered = [record for record in filtered if cls.matches(record.get(field), operator, expected)]
        return filtered

    @classmethod
    def apply_period_filter(cls, records, mode, filter_config, period):
        if mode == "all_time" or not period:
            return list(records)
        date_field = (filter_config or {}).get("date_field_id")
        if not date_field:
            return list(records)
        start = period.get("period_start")
        end = period.get("period_end")
        if not start or not end:
            return list(records)
        return [record for record in records if start <= str(record.get(date_field, "")) <= end]

    @classmethod
    def apply_unicity(cls, records, unicity_field):
        if not unicity_field:
            return list(records)
        seen = set()
        unique_records = []
        for record in records:
            key = record.get(unicity_field)
            if key in seen:
                continue
            seen.add(key)
            unique_records.append(record)
        return unique_records

    @classmethod
    def matches(cls, actual, operator, expected):
        if operator == "eq":
            return actual == expected
        if operator == "neq":
            return actual != expected
        if operator == "in":
            return actual in (expected or [])
        if operator == "gt":
            return cls.decimal_value(actual) > cls.decimal_value(expected)
        if operator == "gte":
            return cls.decimal_value(actual) >= cls.decimal_value(expected)
        if operator == "lt":
            return cls.decimal_value(actual) < cls.decimal_value(expected)
        if operator == "lte":
            return cls.decimal_value(actual) <= cls.decimal_value(expected)
        return False

    @staticmethod
    def decimal_value(value):
        try:
            return Decimal(str(value or "0"))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise IndicatorCalculationError(f"Invalid numeric value: {value}") from exc
