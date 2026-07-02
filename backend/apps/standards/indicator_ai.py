"""AI assistance for Performance Indicators.

Follows the platform's deterministic AI-assistant pattern (see
apps.reports.views generate_* helpers): prompt-token matching against curated
templates, with reviewable output and the shared sensitive-prompt guardrail.
Swap `suggest_indicators` / `generate_formula` internals for a real LLM client
without changing the API surface.
"""

import re
from decimal import Decimal

from .indicator_pi import resolve_effective_target, resolve_performance_band, variance_from_target
from .models import KPITargetDirection


def _prompt_words(prompt):
    return {word for word in re.split(r"[^a-z0-9]+", (prompt or "").lower()) if word}


def assert_indicator_ai_prompt_safe(prompt, *, actor, request, target, context):
    """Reuse the analytics AI guardrail (sensitive terms + audit on block)."""
    from apps.reports.views import assert_ai_prompt_safe

    assert_ai_prompt_safe(prompt, sensitive_fields=None, actor=actor, request=request, target=target, context=context)


SUGGESTION_LIBRARY = [
    {
        "keywords": {"certificate", "coverage", "certification", "certified"},
        "name": "Certificate Coverage Rate",
        "code": "CERT_COVERAGE_RATE",
        "category": "coverage",
        "formula_type": "percentage",
        "unit_of_measurement": "percentage",
        "target_direction": "higher_better",
        "data_source": "certificate_records",
        "description": "Active certificates as a share of registered food handlers.",
    },
    {
        "keywords": {"inspection", "inspections", "inspect"},
        "name": "Inspection Completion Rate",
        "code": "INSPECTION_COMPLETION_RATE",
        "category": "inspections",
        "formula_type": "percentage",
        "unit_of_measurement": "percentage",
        "target_direction": "higher_better",
        "data_source": "inspections",
        "description": "Completed inspections as a share of scheduled inspections.",
    },
    {
        "keywords": {"turnaround", "time", "delay", "duration", "days"},
        "name": "Certificate Issuance Turnaround Time",
        "code": "CERT_TURNAROUND_TIME",
        "category": "timeliness",
        "formula_type": "average_duration",
        "unit_of_measurement": "days",
        "target_direction": "lower_better",
        "data_source": "certificate_records",
        "description": "Average days from assessment completion to certificate issuance.",
    },
    {
        "keywords": {"expired", "expiry", "renewal", "expiring"},
        "name": "Expired Certificate Rate",
        "code": "EXPIRED_CERT_RATE",
        "category": "compliance",
        "formula_type": "percentage",
        "unit_of_measurement": "percentage",
        "target_direction": "lower_better",
        "data_source": "certificate_records",
        "description": "Expired certificates as a share of all issued certificates.",
    },
    {
        "keywords": {"facility", "facilities", "accreditation", "accredited"},
        "name": "Accredited Facility Coverage Rate",
        "code": "FACILITY_COVERAGE_RATE",
        "category": "capacity",
        "formula_type": "percentage",
        "unit_of_measurement": "percentage",
        "target_direction": "higher_better",
        "data_source": "facility_records",
        "description": "Approved facilities as a share of target facility coverage.",
    },
    {
        "keywords": {"form", "forms", "survey", "response", "reporting"},
        "name": "Forms Response Rate",
        "code": "FORMS_RESPONSE_RATE",
        "category": "governance",
        "formula_type": "percentage",
        "unit_of_measurement": "percentage",
        "target_direction": "higher_better",
        "data_source": "manual",
        "description": "Submitted form responses as a share of assigned forms.",
    },
    {
        "keywords": {"revenue", "payment", "payments", "collection"},
        "name": "Revenue Collection Rate",
        "code": "REVENUE_COLLECTION_RATE",
        "category": "finance",
        "formula_type": "percentage",
        "unit_of_measurement": "percentage",
        "target_direction": "higher_better",
        "data_source": "payments",
        "description": "Collected revenue as a share of expected revenue.",
    },
]


def suggest_indicators(prompt, *, limit=3):
    """Return reviewable indicator suggestions matched from the curated library."""
    words = _prompt_words(prompt)
    scored = []
    for template in SUGGESTION_LIBRARY:
        overlap = len(words & template["keywords"])
        if overlap:
            scored.append((overlap, template))
    scored.sort(key=lambda item: -item[0])
    matches = [template for _, template in scored[:limit]] or SUGGESTION_LIBRARY[:limit]
    return [
        {
            **{key: value for key, value in template.items() if key != "keywords"},
            "requires_review": True,
            "reasoning": [
                "Matched your prompt against the FoodCert indicator template library.",
                "Review the formula, target, and thresholds before publishing.",
            ],
        }
        for template in matches
    ]


def generate_formula(prompt):
    """Draft a machine-readable formula config for review from a free-text prompt."""
    words = _prompt_words(prompt)
    if words & {"time", "turnaround", "duration", "days", "delay"}:
        calculation_type = "average"
        unit = "days"
        direction = "lower_better"
    elif words & {"count", "number", "total", "volume"}:
        calculation_type = "count"
        unit = "count"
        direction = "higher_better"
    else:
        calculation_type = "percentage"
        unit = "percentage"
        direction = "higher_better"

    if words & {"inspection", "inspections"}:
        data_source = "inspections"
        numerator_hint = "completed inspections"
        denominator_hint = "scheduled inspections"
    elif words & {"facility", "facilities", "accreditation"}:
        data_source = "facility_records"
        numerator_hint = "approved facilities"
        denominator_hint = "all registered facilities"
    elif words & {"payment", "revenue", "collection"}:
        data_source = "payments"
        numerator_hint = "successful payments"
        denominator_hint = "expected payments"
    else:
        data_source = "certificate_records"
        numerator_hint = "active certificates"
        denominator_hint = "registered food handlers"

    formula = {
        "calculation_type": calculation_type,
        "data_source": data_source,
        "unit_of_measurement": unit,
        "target_direction": direction,
        "numerator_definition": {"description": numerator_hint} if calculation_type == "percentage" else {},
        "denominator_definition": {"description": denominator_hint} if calculation_type == "percentage" else {},
        "requires_review": True,
        "reasoning": [
            f"Interpreted the prompt as a {calculation_type} indicator over the {data_source} dataset.",
            "Denominator-zero periods are reported as no-data rather than zero.",
            "Review and adjust before saving — AI output is a draft, not a definition.",
        ],
    }
    return formula


def explain_result(indicator):
    """Deterministic narrative for an indicator's latest performance."""
    values = list(indicator.values.order_by("-period_end", "-created_at")[:6])
    latest = values[0] if values else None
    target = resolve_effective_target(indicator)

    if latest is None:
        return {
            "indicator_code": indicator.indicator_code,
            "narrative": f"{indicator.indicator_name} has no recorded results yet, so performance cannot be assessed.",
            "facts": {"target": str(target) if target is not None else None},
        }

    observed = latest.cumulative_value_numeric or latest.progress_value_numeric
    band = resolve_performance_band(indicator, observed)
    variance = variance_from_target(observed, target)

    trend = "stable"
    if len(values) >= 2:
        earlier = values[-1].cumulative_value_numeric or values[-1].progress_value_numeric
        if observed is not None and earlier is not None:
            if Decimal(observed) > Decimal(earlier):
                trend = "improving" if indicator.target_direction != KPITargetDirection.LOWER_BETTER else "worsening"
            elif Decimal(observed) < Decimal(earlier):
                trend = "declining" if indicator.target_direction != KPITargetDirection.LOWER_BETTER else "improving"

    sentences = [
        f"{indicator.indicator_name} recorded {observed} {indicator.unit_of_measurement or ''} for the period ending {latest.period_end:%Y-%m-%d}.".strip(),
    ]
    if target is not None:
        comparison = "above" if variance is not None and variance > 0 else "below" if variance is not None and variance < 0 else "at"
        sentences.append(f"That is {comparison} the target of {target} (variance {variance}).")
    if band:
        sentences.append(f"The result falls in the {band['label']} band ({band['severity']}). {band.get('action_recommendation') or ''}".strip())
    sentences.append(f"The trend over the last {len(values)} periods is {trend}.")

    return {
        "indicator_code": indicator.indicator_code,
        "narrative": " ".join(sentences),
        "facts": {
            "latest_value": str(observed) if observed is not None else None,
            "target": str(target) if target is not None else None,
            "variance": str(variance) if variance is not None else None,
            "band": band["band_name"] if band else None,
            "severity": band["severity"] if band else None,
            "trend": trend,
            "periods_analysed": len(values),
        },
    }
