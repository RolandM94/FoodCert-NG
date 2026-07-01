"""Performance Indicators layer: targets, thresholds, adoption, cloning, bands.

Builds the Federal-to-State standardisation behaviour on top of the existing
standards.MEIndicator engine per the Performance Indicators PRD.
"""

from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.locations.models import State

from .models import (
    IndicatorAdoption,
    IndicatorAdoptionStatus,
    IndicatorLifecycleStatus,
    IndicatorScopeType,
    IndicatorTarget,
    IndicatorTargetSource,
    IndicatorThreshold,
    IndicatorVisibility,
    MEIndicator,
    MEIndicatorDataSource,
    IndicatorOwnerType,
    StandardStatus,
)


def _to_decimal(value):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def resolve_effective_target(indicator, *, scope_type=IndicatorScopeType.NATIONAL, scope_id=""):
    """Return the effective target value for a scope, inheriting from national when unset."""
    scoped = indicator.targets.filter(is_active=True, scope_type=scope_type, scope_id=scope_id).first()
    if scoped:
        return scoped.target_value
    national = indicator.targets.filter(is_active=True, scope_type=IndicatorScopeType.NATIONAL).first()
    if national:
        return national.target_value
    return indicator.target_value


def resolve_performance_band(indicator, value, *, scope_type=IndicatorScopeType.NATIONAL, scope_id=""):
    """Map a calculated value to a threshold band, falling back to national bands."""
    value = _to_decimal(value)
    if value is None:
        return None
    bands = list(indicator.thresholds.filter(scope_type=scope_type, scope_id=scope_id))
    if not bands:
        bands = list(indicator.thresholds.filter(scope_type=IndicatorScopeType.NATIONAL))
    for band in bands:
        low_ok = band.min_value is None or value >= band.min_value
        high_ok = band.max_value is None or value <= band.max_value
        if low_ok and high_ok:
            return {
                "band_name": band.band_name,
                "severity": band.severity,
                "color": band.color,
                "label": band.label or band.band_name,
                "action_recommendation": band.action_recommendation,
            }
    return None


def variance_from_target(value, target):
    value = _to_decimal(value)
    target = _to_decimal(target)
    if value is None or target is None:
        return None
    return value - target


class IndicatorLifecycleService:
    @classmethod
    @transaction.atomic
    def publish(cls, indicator, actor, request=None):
        indicator.lifecycle_status = IndicatorLifecycleStatus.ACTIVE
        indicator.status = StandardStatus.ACTIVE
        indicator.published_by = actor
        indicator.published_at = timezone.now()
        if indicator.visibility == IndicatorVisibility.FEDERAL_PRIVATE:
            indicator.visibility = IndicatorVisibility.FEDERAL_STANDARD
        indicator.save(update_fields=[
            "lifecycle_status", "status", "published_by", "published_at", "visibility", "updated_at",
        ])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=indicator,
                   metadata={"event": "indicator_published"}, request=request)
        return indicator

    @classmethod
    @transaction.atomic
    def set_lifecycle(cls, indicator, actor, new_status, request=None):
        indicator.lifecycle_status = new_status
        if new_status == IndicatorLifecycleStatus.ACTIVE:
            indicator.status = StandardStatus.ACTIVE
        elif new_status in {IndicatorLifecycleStatus.PAUSED, IndicatorLifecycleStatus.DEPRECATED}:
            indicator.status = StandardStatus.INACTIVE
        elif new_status == IndicatorLifecycleStatus.ARCHIVED:
            indicator.status = StandardStatus.ARCHIVED
        indicator.save(update_fields=["lifecycle_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=indicator,
                   metadata={"event": "indicator_lifecycle_changed", "status": new_status}, request=request)
        return indicator


class IndicatorAdoptionService:
    @classmethod
    @transaction.atomic
    def share_to_states(cls, indicator, actor, state_ids=None, request=None):
        indicator.visibility = IndicatorVisibility.FEDERAL_SHARED if state_ids else IndicatorVisibility.FEDERAL_STANDARD
        indicator.save(update_fields=["visibility", "updated_at"])
        states = State.objects.filter(id__in=state_ids) if state_ids else State.objects.all()
        created = 0
        for state in states:
            _, was_created = IndicatorAdoption.objects.get_or_create(
                federal_indicator=indicator, state=state,
                defaults={"adoption_status": IndicatorAdoptionStatus.AVAILABLE,
                          "adopted_version": indicator.version},
            )
            created += int(was_created)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=indicator,
                   metadata={"event": "indicator_shared_to_states", "state_count": states.count()}, request=request)
        return {"shared_with": states.count(), "new_adoption_records": created}

    @classmethod
    @transaction.atomic
    def adopt(cls, federal_indicator, state, actor, request=None):
        adoption, _ = IndicatorAdoption.objects.update_or_create(
            federal_indicator=federal_indicator, state=state,
            defaults={
                "adoption_status": IndicatorAdoptionStatus.ADOPTED,
                "adopted_version": federal_indicator.version,
                "state_target_override_enabled": federal_indicator.allow_state_target_override,
                "adopted_by": actor,
                "adopted_at": timezone.now(),
                "last_synced_at": timezone.now(),
            },
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=federal_indicator, state=state,
                   metadata={"event": "indicator_adopted", "state_id": str(state.id)}, request=request)
        return adoption

    @classmethod
    @transaction.atomic
    def clone_for_state(cls, federal_indicator, state, actor, request=None):
        if not federal_indicator.allow_state_clone:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("This federal indicator does not allow state cloning.")

        clone = MEIndicator.objects.create(
            policy_version=federal_indicator.policy_version,
            indicator_name=f"{federal_indicator.indicator_name} ({state.code or state.name})",
            indicator_code=f"{federal_indicator.indicator_code}-{state.code or state.id}",
            description=federal_indicator.description,
            kpi_type=federal_indicator.kpi_type,
            unit_of_measurement=federal_indicator.unit_of_measurement,
            input_mode=federal_indicator.input_mode,
            record_input_type=federal_indicator.record_input_type,
            progress_cumulative_relationship=federal_indicator.progress_cumulative_relationship,
            target_direction=federal_indicator.target_direction,
            calculation_type=federal_indicator.calculation_type,
            calculation_source=federal_indicator.calculation_source,
            numerator_definition=federal_indicator.numerator_definition,
            denominator_definition=federal_indicator.denominator_definition,
            formula_config=federal_indicator.formula_config,
            data_source=federal_indicator.data_source,
            reporting_frequency=federal_indicator.reporting_frequency,
            target_value=federal_indicator.target_value,
            threshold_config=federal_indicator.threshold_config,
            visualization_type=federal_indicator.visualization_type,
            category=federal_indicator.category,
            owner_type=IndicatorOwnerType.STATE,
            owner_state=state,
            visibility=IndicatorVisibility.STATE_OWNED,
            lifecycle_status=IndicatorLifecycleStatus.DRAFT,
            version="1.0",
            source_indicator=federal_indicator,
            allow_state_target_override=True,
            created_by=actor,
        )
        for target in federal_indicator.targets.all():
            IndicatorTarget.objects.create(
                indicator=clone, scope_type=target.scope_type, scope_id=target.scope_id,
                target_value=target.target_value, target_unit=target.target_unit,
                source=IndicatorTargetSource.CUSTOM, set_by=actor,
            )
        for band in federal_indicator.thresholds.all():
            IndicatorThreshold.objects.create(
                indicator=clone, scope_type=band.scope_type, scope_id=band.scope_id,
                band_name=band.band_name, severity=band.severity,
                min_value=band.min_value, max_value=band.max_value,
                color=band.color, label=band.label, action_recommendation=band.action_recommendation,
            )
        for config in federal_indicator.data_source_configs.all():
            MEIndicatorDataSource.objects.create(
                indicator=clone, source_type=config.source_type, source_id=config.source_id,
                calculation_method=config.calculation_method, value_field_id=config.value_field_id,
                numerator_config_json=config.numerator_config_json,
                denominator_config_json=config.denominator_config_json,
                filter_config_json=config.filter_config_json,
                unicity_field_id=config.unicity_field_id, period_filter_mode=config.period_filter_mode,
            )

        IndicatorAdoption.objects.update_or_create(
            federal_indicator=federal_indicator, state=state,
            defaults={
                "adoption_status": IndicatorAdoptionStatus.CLONED,
                "adopted_version": federal_indicator.version,
                "cloned_indicator": clone,
                "adopted_by": actor,
                "adopted_at": timezone.now(),
                "last_synced_at": timezone.now(),
            },
        )
        log_action(action=AuditAction.CREATE, actor=actor, target=clone, state=state,
                   metadata={"event": "indicator_cloned_for_state", "source_indicator": str(federal_indicator.id)},
                   request=request)
        return clone
