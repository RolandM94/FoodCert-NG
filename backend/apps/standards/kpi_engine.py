from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from .models import (
    IndicatorCalculationStatus,
    IndicatorValueSource,
    KPIInputMode,
    MEIndicator,
    MEIndicatorCalculationLog,
    MEIndicatorValue,
    MEIndicatorValueHistory,
)
from .services import ActivePolicyRuleError, ActivePolicyRuleService


class KPIEngineError(ValueError):
    pass


AUTOMATIC_SOURCE_REFERENCE = "automatic-kpi-engine"
DATA_COMPLETENESS_REQUIRED_FIELDS = (
    "full_name",
    "date_of_birth",
    "gender",
    "nin",
    "phone",
    "email",
    "home_address",
    "state_id",
    "food_handler_category",
)


class FoodHandlersKpiCalculationService:
    @classmethod
    def calculate_kpi(cls, kpi_id, filters=None, actor=None):
        indicator = MEIndicator.objects.select_related("policy_version").get(id=kpi_id)
        if indicator.input_mode not in {KPIInputMode.AUTOMATIC, KPIInputMode.HYBRID}:
            raise KPIEngineError("Only automatic and hybrid KPIs can be auto-calculated.")

        normalized_filters = cls.normalize_filters(filters)
        period = cls.resolve_period(indicator.reporting_frequency, normalized_filters)
        policy_context = {
            "policy_version_id": str(indicator.policy_version_id) if indicator.policy_version_id else "",
            "policy_standard_code": indicator.policy_standard_code or "",
            "policy_standard_id": "",
            "parameters": {},
        }

        try:
            policy_context = cls.resolve_policy_context(indicator)
            result = cls.calculate_for_indicator(indicator, normalized_filters, period, policy_context)
            value = cls.store_result(
                indicator=indicator,
                period=period,
                result=result,
                filters=normalized_filters,
                actor=actor,
                policy_context=policy_context,
            )
        except Exception as exc:
            cls.create_calculation_log(
                indicator=indicator,
                period=period,
                result=None,
                filters=normalized_filters,
                actor=actor,
                policy_context=policy_context,
                status=IndicatorCalculationStatus.FAILED,
                error_message=str(exc),
            )
            if isinstance(exc, (KPIEngineError, ActivePolicyRuleError)):
                raise
            raise KPIEngineError(str(exc)) from exc

        return {
            **result,
            "indicator_id": str(indicator.id),
            "value_id": str(value.id),
            "period_start": period["period_start"].isoformat(),
            "period_end": period["period_end"].isoformat(),
        }

    @classmethod
    def calculate_for_indicator(cls, indicator, filters, period, policy_context=None):
        source = indicator.calculation_source or ""
        if source == "system_required_fields":
            return cls.calculate_data_completeness_score(filters, period=period)
        if source == "certificates" and indicator.indicator_code == "ME-EXPIRED-RATE":
            return cls.calculate_expired_certificate_rate(filters, period=period, policy_context=policy_context)
        if source == "medical_facilities":
            return cls.calculate_facility_accreditation_compliance(filters, period=period, policy_context=policy_context)
        if source == "certificates":
            return cls.calculate_food_handler_certification_rate(filters, period=period, policy_context=policy_context)
        if source == "qr_verification_logs":
            return cls.calculate_qr_verification_failure_rate(filters, period=period, policy_context=policy_context)
        if source == "return_to_work_clearances":
            return cls.calculate_return_to_work_clearance_rate(filters, period=period, policy_context=policy_context)
        raise KPIEngineError(f"Unsupported KPI calculation source: {source or 'unknown'}.")

    @classmethod
    def get_kpi_source_records(cls, kpi_id, filters=None):
        indicator = MEIndicator.objects.select_related("policy_version").get(id=kpi_id)
        normalized_filters = cls.normalize_filters(filters)
        period = cls.resolve_period(indicator.reporting_frequency, normalized_filters)
        policy_context = cls.resolve_policy_context(indicator)
        result = cls.calculate_for_indicator(indicator, normalized_filters, period, policy_context)
        return {
            "indicator_id": str(indicator.id),
            "indicator_code": indicator.indicator_code,
            "period_start": period["period_start"].isoformat(),
            "period_end": period["period_end"].isoformat(),
            "records": result["records"],
            "value": str(result["value"]),
            "numerator": str(result["numerator"]) if result["numerator"] is not None else None,
            "denominator": str(result["denominator"]) if result["denominator"] is not None else None,
        }

    @classmethod
    def recalculate_automatic_kpis(cls, filters=None, actor=None):
        indicators = MEIndicator.objects.filter(
            input_mode__in=[KPIInputMode.AUTOMATIC, KPIInputMode.HYBRID],
            status="active",
        ).order_by("indicator_code")
        summary = {"success": [], "failed": []}
        for indicator in indicators:
            try:
                result = cls.calculate_kpi(indicator.id, filters=filters, actor=actor)
            except Exception as exc:
                summary["failed"].append({"indicator_id": str(indicator.id), "indicator_code": indicator.indicator_code, "error": str(exc)})
            else:
                summary["success"].append({
                    "indicator_id": str(indicator.id),
                    "indicator_code": indicator.indicator_code,
                    "value": str(result["value"]),
                })
        return summary

    @classmethod
    def calculate_data_completeness_score(cls, filters, *, period=None, policy_context=None):
        from apps.food_handlers.models import FoodHandlerProfile

        handlers = cls.apply_food_handler_filters(FoodHandlerProfile.objects.select_related("state", "lga", "employer"), filters)
        records = []
        completed_fields = 0
        for handler in handlers:
            missing = []
            present = 0
            for field in DATA_COMPLETENESS_REQUIRED_FIELDS:
                value = getattr(handler, field, "")
                if value in (None, "", []):
                    missing.append(field.replace("_id", ""))
                else:
                    present += 1
            completed_fields += present
            records.append({
                "food_handler_id": str(handler.id),
                "food_handler_name": handler.full_name,
                "state": handler.state.name if handler.state_id else "",
                "lga": handler.lga.name if handler.lga_id else "",
                "category": handler.food_handler_category,
                "completed_required_fields": present,
                "total_required_fields": len(DATA_COMPLETENESS_REQUIRED_FIELDS),
                "missing_fields": missing,
            })
        total_required_fields = len(DATA_COMPLETENESS_REQUIRED_FIELDS) * len(records)
        value = cls.percentage(completed_fields, total_required_fields) if total_required_fields else Decimal("0")
        return cls.result(value=value, numerator=Decimal(completed_fields), denominator=Decimal(total_required_fields), records=records)

    @classmethod
    def calculate_expired_certificate_rate(cls, filters, *, period=None, policy_context=None):
        from apps.certificates.models import Certificate

        certificates = cls.apply_certificate_filters(Certificate.objects.select_related("food_handler__state", "facility"), filters, period=period)
        issued = []
        expired = 0
        for certificate in certificates:
            effective_status = certificate.effective_status
            if certificate.status in {"pending_validation", "rejected"}:
                continue
            issued.append(certificate)
            if effective_status == "expired":
                expired += 1
        records = [
            {
                "certificate_id": str(certificate.id),
                "certificate_number": certificate.certificate_number,
                "food_handler_name": certificate.food_handler.full_name,
                "issue_date": certificate.issue_date.isoformat(),
                "expiry_date": certificate.expiry_date.isoformat(),
                "status": certificate.effective_status,
                "state": certificate.issuing_state.name if certificate.issuing_state_id else "",
                "facility": certificate.facility.facility_name if certificate.facility_id else "",
            }
            for certificate in issued
        ]
        return cls.result(
            value=cls.percentage(expired, len(issued)) if issued else Decimal("0"),
            numerator=Decimal(expired),
            denominator=Decimal(len(issued)),
            records=records,
        )

    @classmethod
    def calculate_facility_accreditation_compliance(cls, filters, *, period=None, policy_context=None):
        from apps.facilities.models import AccreditationStatus, MedicalFacility

        facilities = cls.apply_facility_filters(MedicalFacility.objects.select_related("state", "lga"), filters, period=period)
        compliant_statuses = {AccreditationStatus.APPROVED}
        records = []
        compliant = 0
        for facility in facilities:
            is_compliant = facility.accreditation_status in compliant_statuses and bool(
                facility.accreditation_expiry_date and facility.accreditation_expiry_date >= timezone.localdate()
            )
            compliant += 1 if is_compliant else 0
            records.append({
                "facility_id": str(facility.id),
                "facility_name": facility.facility_name,
                "state": facility.state.name if facility.state_id else "",
                "accreditation_issue_date": facility.accreditation_start_date.isoformat() if facility.accreditation_start_date else "",
                "accreditation_expiry_date": facility.accreditation_expiry_date.isoformat() if facility.accreditation_expiry_date else "",
                "status": facility.accreditation_status,
                "is_compliant": is_compliant,
            })
        return cls.result(
            value=cls.percentage(compliant, len(records)) if records else Decimal("0"),
            numerator=Decimal(compliant),
            denominator=Decimal(len(records)),
            records=records,
        )

    @classmethod
    def calculate_food_handler_certification_rate(cls, filters, *, period=None, policy_context=None):
        from apps.certificates.models import Certificate
        from apps.food_handlers.models import FoodHandlerProfile

        handlers = cls.apply_food_handler_filters(FoodHandlerProfile.objects.select_related("state", "lga", "employer"), filters)
        certificates = cls.apply_certificate_filters(
            Certificate.objects.select_related("food_handler", "facility", "food_handler__state", "food_handler__lga"),
            filters,
            period=period,
        )
        valid_handler_ids = {
            str(certificate.food_handler_id)
            for certificate in certificates
            if certificate.effective_status == "active"
        }
        latest_by_handler = {}
        for certificate in certificates.order_by("-issue_date", "-created_at"):
            latest_by_handler.setdefault(str(certificate.food_handler_id), certificate)
        records = []
        certified = 0
        for handler in handlers:
            latest = latest_by_handler.get(str(handler.id))
            is_certified = str(handler.id) in valid_handler_ids
            certified += 1 if is_certified else 0
            records.append({
                "food_handler_id": str(handler.id),
                "food_handler_name": handler.full_name,
                "food_handler_category": handler.food_handler_category,
                "state": handler.state.name if handler.state_id else "",
                "lga": handler.lga.name if handler.lga_id else "",
                "facility": latest.facility.facility_name if latest and latest.facility_id else "",
                "certificate_id": str(latest.id) if latest else "",
                "certificate_issue_date": latest.issue_date.isoformat() if latest else "",
                "certificate_expiry_date": latest.expiry_date.isoformat() if latest else "",
                "certificate_status": latest.effective_status if latest else "not_certified",
                "is_certified": is_certified,
            })
        return cls.result(
            value=cls.percentage(certified, len(records)) if records else Decimal("0"),
            numerator=Decimal(certified),
            denominator=Decimal(len(records)),
            records=records,
        )

    @classmethod
    def calculate_qr_verification_failure_rate(cls, filters, *, period=None, policy_context=None):
        from apps.certificates.models import CertificateVerificationLog

        if policy_context and not policy_context["parameters"].get("requires_qr_code"):
            raise KPIEngineError("Active policy does not require QR verification for this KPI.")
        logs = cls.apply_verification_filters(
            CertificateVerificationLog.objects.select_related("certificate__facility", "certificate__issuing_state"),
            filters,
            period=period,
        )
        failures = []
        records = []
        for log in logs:
            is_failure = log.result != "valid"
            if is_failure:
                failures.append(log)
            certificate = log.certificate
            records.append({
                "verification_timestamp": log.verified_at.isoformat(),
                "certificate_id": str(certificate.id) if certificate else "",
                "certificate_number": certificate.certificate_number if certificate else log.certificate_number_submitted,
                "failure_reason": "" if log.result == "valid" else log.result,
                "verifier_type": log.verifier_type,
                "state": certificate.issuing_state.name if certificate and certificate.issuing_state_id else "",
                "facility": certificate.facility.facility_name if certificate and certificate.facility_id else "",
                "result": log.result,
            })
        return cls.result(
            value=cls.percentage(len(failures), len(records)) if records else Decimal("0"),
            numerator=Decimal(len(failures)),
            denominator=Decimal(len(records)),
            records=records,
        )

    @classmethod
    def calculate_return_to_work_clearance_rate(cls, filters, *, period=None, policy_context=None):
        from apps.illness.models import IllnessReport

        reports = cls.apply_illness_filters(
            IllnessReport.objects.select_related("food_handler__state", "employer", "reviewed_by_doctor"),
            filters,
            period=period,
        ).filter(clearance_required=True)
        records = []
        cleared = 0
        for report in reports:
            is_cleared = report.clearance_status == "cleared"
            cleared += 1 if is_cleared else 0
            records.append({
                "illness_report_id": str(report.id),
                "food_handler_name": report.food_handler.full_name,
                "illness_reason": report.suspected_condition,
                "exclusion_start_date": report.exclusion_start_date.isoformat() if report.exclusion_start_date else "",
                "required_clearance_date": report.earliest_return_date.isoformat() if report.earliest_return_date else "",
                "clearance_date": report.cleared_at.date().isoformat() if report.cleared_at else "",
                "clearance_status": report.clearance_status,
                "medical_facility": "",
                "approving_practitioner": report.reviewed_by_doctor.get_full_name() if report.reviewed_by_doctor_id else "",
            })
        return cls.result(
            value=cls.percentage(cleared, len(records)) if records else Decimal("0"),
            numerator=Decimal(cleared),
            denominator=Decimal(len(records)),
            records=records,
        )

    @classmethod
    def store_result(cls, *, indicator, period, result, filters, actor, policy_context):
        from .indicator_pi import resolve_effective_target, resolve_performance_band, variance_from_target

        now = timezone.now()
        effective_target = resolve_effective_target(indicator)
        band = resolve_performance_band(indicator, result["value"])
        value, created = MEIndicatorValue.objects.update_or_create(
            indicator=indicator,
            period_start=period["period_start"],
            period_end=period["period_end"],
            value_source=IndicatorValueSource.AUTOMATED,
            source_reference_id=AUTOMATIC_SOURCE_REFERENCE,
            defaults={
                "progress_value_numeric": result["value"],
                "cumulative_value_numeric": result["value"],
                "calculation_snapshot_json": result["snapshot"],
                "target_value": effective_target,
                "variance_from_target": variance_from_target(result["value"], effective_target),
                "performance_band": band["band_name"] if band else "",
                "performance_severity": band["severity"] if band else "",
                "notes": "Generated by Food Handlers KPI engine.",
                "created_by": actor,
            },
        )
        indicator.latest_value = result["value"]
        indicator.last_calculated_at = now
        indicator.achievement_value = cls.compute_achievement_value(indicator, result["value"])
        indicator.save(update_fields=["latest_value", "last_calculated_at", "achievement_value", "updated_at"])
        cls.create_value_history(value=value, actor=actor, action="calculated" if created else "recalculated")
        cls.create_calculation_log(
            indicator=indicator,
            period=period,
            result=result,
            filters=filters,
            actor=actor,
            policy_context=policy_context,
            status=IndicatorCalculationStatus.SUCCESS,
            error_message="",
        )
        return value

    @classmethod
    def create_calculation_log(cls, *, indicator, period, result, filters, actor, policy_context, status, error_message):
        snapshot = (result or {}).get("snapshot", {})
        policy_version_id = (policy_context or {}).get("policy_version_id")
        MEIndicatorCalculationLog.objects.create(
            indicator=indicator,
            period_start=period["period_start"],
            period_end=period["period_end"],
            calculated_value=(result or {}).get("value"),
            numerator_value=(result or {}).get("numerator"),
            denominator_value=(result or {}).get("denominator"),
            filters_used=filters,
            policy_version_id=policy_version_id,
            policy_standard_code=(policy_context or {}).get("policy_standard_code", ""),
            policy_standard_id=(policy_context or {}).get("policy_standard_id", ""),
            calculated_by=actor,
            calculation_status=status,
            error_message=error_message,
            source_record_count=len((result or {}).get("records", [])),
            snapshot_json=snapshot,
        )

    @classmethod
    def create_value_history(cls, *, value, actor, action):
        snapshot = {
            "period_start": value.period_start.isoformat(),
            "period_end": value.period_end.isoformat(),
            "progress_value_numeric": str(value.progress_value_numeric) if value.progress_value_numeric is not None else None,
            "cumulative_value_numeric": str(value.cumulative_value_numeric) if value.cumulative_value_numeric is not None else None,
            "approval_status": value.approval_status,
            "notes": value.notes,
        }
        MEIndicatorValueHistory.objects.create(
            value=value,
            action=action,
            from_status="",
            to_status=value.approval_status,
            snapshot_json=snapshot,
            actor=actor,
        )

    @classmethod
    def resolve_policy_context(cls, indicator):
        if not indicator.policy_standard_code:
            return {
                "policy_version_id": str(indicator.policy_version_id) if indicator.policy_version_id else "",
                "policy_standard_code": "",
                "policy_standard_id": "",
                "parameters": {},
            }
        return ActivePolicyRuleService.get_active_policy_standard_by_code(indicator.policy_standard_code)

    @classmethod
    def resolve_period(cls, reporting_frequency, filters):
        start = cls.parse_date(filters.get("period_start") or filters.get("date_from"))
        end = cls.parse_date(filters.get("period_end") or filters.get("date_to"))
        if start and end:
            return {"period_start": start, "period_end": end}

        today = timezone.localdate()
        if reporting_frequency == "monthly":
            period_start = today.replace(day=1)
            next_month = (period_start.replace(day=28) + timedelta(days=4)).replace(day=1)
            period_end = next_month - timedelta(days=1)
        elif reporting_frequency == "quarterly":
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            period_start = date(today.year, quarter_start_month, 1)
            if quarter_start_month == 10:
                period_end = date(today.year, 12, 31)
            else:
                period_end = date(today.year, quarter_start_month + 3, 1) - timedelta(days=1)
        elif reporting_frequency == "weekly":
            period_start = today - timedelta(days=today.weekday())
            period_end = period_start + timedelta(days=6)
        elif reporting_frequency == "annual":
            period_start = date(today.year, 1, 1)
            period_end = date(today.year, 12, 31)
        else:
            period_start = today.replace(day=1)
            next_month = (period_start.replace(day=28) + timedelta(days=4)).replace(day=1)
            period_end = next_month - timedelta(days=1)
        return {"period_start": period_start, "period_end": period_end}

    @classmethod
    def normalize_filters(cls, filters):
        filters = dict(filters or {})
        normalized = {}
        for key, value in filters.items():
            if value in (None, "", []):
                continue
            normalized[key] = value
        return normalized

    @classmethod
    def apply_food_handler_filters(cls, queryset, filters):
        if filters.get("state_id"):
            queryset = queryset.filter(state_id=filters["state_id"])
        if filters.get("lga_id"):
            queryset = queryset.filter(lga_id=filters["lga_id"])
        if filters.get("food_handler_category"):
            queryset = queryset.filter(food_handler_category=filters["food_handler_category"])
        if filters.get("establishment_type"):
            queryset = queryset.filter(employer__establishment_category=filters["establishment_type"])
        if filters.get("facility_id"):
            queryset = queryset.filter(
                models.Q(certificates__facility_id=filters["facility_id"]) |
                models.Q(assessments__facility_id=filters["facility_id"])
            )
        if filters.get("date_from"):
            queryset = queryset.filter(created_at__date__gte=cls.parse_date(filters["date_from"]))
        if filters.get("date_to"):
            queryset = queryset.filter(created_at__date__lte=cls.parse_date(filters["date_to"]))
        return queryset.distinct()

    @classmethod
    def apply_certificate_filters(cls, queryset, filters, *, period=None):
        if filters.get("state_id"):
            queryset = queryset.filter(issuing_state_id=filters["state_id"])
        if filters.get("lga_id"):
            queryset = queryset.filter(food_handler__lga_id=filters["lga_id"])
        if filters.get("facility_id"):
            queryset = queryset.filter(facility_id=filters["facility_id"])
        if filters.get("food_handler_category"):
            queryset = queryset.filter(food_handler__food_handler_category=filters["food_handler_category"])
        if filters.get("establishment_type"):
            queryset = queryset.filter(food_handler__employer__establishment_category=filters["establishment_type"])
        if filters.get("certificate_status"):
            queryset = queryset.filter(status=filters["certificate_status"])
        if period:
            queryset = queryset.filter(issue_date__gte=period["period_start"], issue_date__lte=period["period_end"])
        return queryset.distinct()

    @classmethod
    def apply_facility_filters(cls, queryset, filters, *, period=None):
        if filters.get("state_id"):
            queryset = queryset.filter(state_id=filters["state_id"])
        if filters.get("lga_id"):
            queryset = queryset.filter(lga_id=filters["lga_id"])
        if filters.get("facility_id"):
            queryset = queryset.filter(id=filters["facility_id"])
        if period:
            queryset = queryset.filter(
                models.Q(accreditation_start_date__isnull=True) | models.Q(accreditation_start_date__lte=period["period_end"])
            )
        return queryset.distinct()

    @classmethod
    def apply_verification_filters(cls, queryset, filters, *, period=None):
        if filters.get("state_id"):
            queryset = queryset.filter(certificate__issuing_state_id=filters["state_id"])
        if filters.get("facility_id"):
            queryset = queryset.filter(certificate__facility_id=filters["facility_id"])
        if filters.get("certificate_status"):
            queryset = queryset.filter(certificate__status=filters["certificate_status"])
        if period:
            start_dt = timezone.make_aware(timezone.datetime.combine(period["period_start"], timezone.datetime.min.time()))
            end_dt = timezone.make_aware(timezone.datetime.combine(period["period_end"], timezone.datetime.max.time()))
            queryset = queryset.filter(verified_at__gte=start_dt, verified_at__lte=end_dt)
        return queryset.distinct()

    @classmethod
    def apply_illness_filters(cls, queryset, filters, *, period=None):
        if filters.get("state_id"):
            queryset = queryset.filter(food_handler__state_id=filters["state_id"])
        if filters.get("lga_id"):
            queryset = queryset.filter(food_handler__lga_id=filters["lga_id"])
        if filters.get("food_handler_category"):
            queryset = queryset.filter(food_handler__food_handler_category=filters["food_handler_category"])
        if filters.get("establishment_type"):
            queryset = queryset.filter(food_handler__employer__establishment_category=filters["establishment_type"])
        if period:
            queryset = queryset.filter(created_at__date__gte=period["period_start"], created_at__date__lte=period["period_end"])
        return queryset.distinct()

    @staticmethod
    def compute_achievement_value(indicator, value):
        if indicator.target_value in (None, Decimal("0")):
            return None
        target = Decimal(indicator.target_value)
        numeric_value = Decimal(value)
        if indicator.target_direction == "lower_better":
            if numeric_value == 0:
                return Decimal("100.00")
            return (target / numeric_value) * Decimal("100")
        return (numeric_value / target) * Decimal("100")

    @staticmethod
    def result(*, value, numerator, denominator, records):
        return {
            "value": value.quantize(Decimal("0.0001")),
            "numerator": None if numerator is None else Decimal(numerator).quantize(Decimal("0.0001")),
            "denominator": None if denominator is None else Decimal(denominator).quantize(Decimal("0.0001")),
            "records": records,
            "snapshot": {
                "value": str(value.quantize(Decimal("0.0001"))),
                "numerator": None if numerator is None else str(Decimal(numerator).quantize(Decimal("0.0001"))),
                "denominator": None if denominator is None else str(Decimal(denominator).quantize(Decimal("0.0001"))),
                "record_count": len(records),
            },
        }

    @staticmethod
    def percentage(numerator, denominator):
        numerator = Decimal(numerator)
        denominator = Decimal(denominator)
        if denominator == 0:
            return Decimal("0")
        return (numerator / denominator) * Decimal("100")

    @staticmethod
    def parse_date(value):
        if isinstance(value, date):
            return value
        if not value:
            return None
        return date.fromisoformat(str(value))
