"""Federal compliance auto-flagging engine.

Scans live platform data for national compliance risks and upserts
ComplianceAlert records. Each detector is idempotent: re-running the scan
updates the metric on an existing open alert rather than creating duplicates.
"""

from django.db.models import Count, Q
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import Certificate, CertificateStatus, CertificateVerificationLog, VerificationResult
from apps.facilities.models import AccreditationStatus, MedicalFacility
from apps.lab_tests.models import LabTest, LabTestStatus
from apps.locations.models import State
from apps.ministries.models import (
    ComplianceAlert,
    ComplianceAlertSeverity,
    ComplianceAlertStatus,
    ComplianceAlertType,
    StateReport,
    StateReportStatus,
)


OPEN_STATUSES = [
    ComplianceAlertStatus.OPEN,
    ComplianceAlertStatus.ACKNOWLEDGED,
    ComplianceAlertStatus.IN_REVIEW,
]

# Tunable thresholds for the auto-flag detectors.
THRESHOLDS = {
    "report_overdue_days": 45,
    "unusual_cert_per_facility_24h": 50,
    "high_facility_suspension_rate": 0.25,
    "high_facility_suspension_min": 3,
    "high_pending_lab_results": 25,
    "high_expired_certificates": 50,
    "verification_failure_window_hours": 24,
    "verification_failure_count": 20,
}

PENDING_LAB_STATUSES = [
    LabTestStatus.REQUESTED,
    LabTestStatus.SAMPLE_COLLECTION_PENDING,
    LabTestStatus.SAMPLE_COLLECTED,
    LabTestStatus.IN_PROGRESS,
]


class ComplianceDetectionService:
    @classmethod
    def scan(cls, *, actor=None):
        """Run every detector and return a summary of upserted alerts."""
        detectors = [
            cls._detect_policy_not_adopted,
            cls._detect_report_overdue,
            cls._detect_unusual_certificate_pattern,
            cls._detect_duplicate_active_certificates,
            cls._detect_high_facility_suspension,
            cls._detect_high_pending_lab_results,
            cls._detect_high_expired_certificates,
            cls._detect_verification_failures,
        ]
        created = 0
        updated = 0
        for detector in detectors:
            c, u = detector()
            created += c
            updated += u
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            metadata={"event": "compliance_scan_run", "created": created, "updated": updated},
        )
        return {"created": created, "updated": updated, "open_alerts": ComplianceAlert.objects.filter(status__in=OPEN_STATUSES).count()}

    # -- upsert helper ---------------------------------------------------

    @classmethod
    def _upsert(cls, *, alert_type, dedupe_key, title, description, severity, state=None, state_id=None, entity_type="", entity_id="", metric_value=None, threshold_value=None, metadata=None):
        if state is not None:
            state_id = state.id
        now = timezone.now()
        existing = ComplianceAlert.objects.filter(
            alert_type=alert_type, dedupe_key=dedupe_key, status__in=OPEN_STATUSES,
        ).first()
        if existing:
            existing.title = title
            existing.description = description
            existing.severity = severity
            existing.state_id = state_id
            existing.entity_type = entity_type
            existing.entity_id = entity_id
            existing.metric_value = metric_value
            existing.threshold_value = threshold_value
            existing.metadata = metadata or {}
            existing.last_detected_at = now
            existing.save(update_fields=[
                "title", "description", "severity", "state", "entity_type",
                "entity_id", "metric_value", "threshold_value", "metadata",
                "last_detected_at", "updated_at",
            ])
            return False
        ComplianceAlert.objects.create(
            alert_type=alert_type,
            dedupe_key=dedupe_key,
            title=title,
            description=description,
            severity=severity,
            status=ComplianceAlertStatus.OPEN,
            state_id=state_id,
            entity_type=entity_type,
            entity_id=entity_id,
            metric_value=metric_value,
            threshold_value=threshold_value,
            metadata=metadata or {},
            auto_generated=True,
            last_detected_at=now,
        )
        return True

    @staticmethod
    def _tally(results):
        created = sum(1 for r in results if r)
        return created, len(results) - created

    # -- detectors -------------------------------------------------------

    @classmethod
    def _detect_policy_not_adopted(cls):
        from apps.standards.models import AcknowledgementStatus, PolicyVersion, PolicyVersionStatus, StateAcknowledgement

        active = PolicyVersion.objects.filter(status=PolicyVersionStatus.ACTIVE).order_by("-published_at").first()
        if not active:
            return 0, 0
        results = []
        pending = StateAcknowledgement.objects.filter(
            policy_version=active,
            status__in=[AcknowledgementStatus.PENDING, AcknowledgementStatus.OVERDUE],
        ).select_related("state")
        for ack in pending:
            severity = ComplianceAlertSeverity.HIGH if ack.status == AcknowledgementStatus.OVERDUE else ComplianceAlertSeverity.MEDIUM
            results.append(cls._upsert(
                alert_type=ComplianceAlertType.POLICY_NOT_ADOPTED,
                dedupe_key=f"policy_not_adopted:{active.id}:{ack.state_id}",
                title=f"{ack.state.name} has not adopted {active.version_code}",
                description=f"State acknowledgement for active policy {active.version_code} is {ack.get_status_display().lower()}.",
                severity=severity,
                state=ack.state,
                entity_type="PolicyVersion",
                entity_id=str(active.id),
                metadata={"policy_version_code": active.version_code, "acknowledgement_status": ack.status},
            ))
        return cls._tally(results)

    @classmethod
    def _detect_report_overdue(cls):
        cutoff = timezone.localdate() - timezone.timedelta(days=THRESHOLDS["report_overdue_days"])
        results = []
        for state in State.objects.all():
            latest = StateReport.objects.filter(state=state).order_by("-reporting_period_end").first()
            overdue = latest is None or latest.reporting_period_end < cutoff
            if not overdue:
                continue
            results.append(cls._upsert(
                alert_type=ComplianceAlertType.REPORT_OVERDUE,
                dedupe_key=f"report_overdue:{state.id}",
                title=f"{state.name} M&E report overdue",
                description=(
                    f"No state report since {latest.reporting_period_end:%Y-%m-%d}." if latest
                    else "No state report has ever been submitted."
                ),
                severity=ComplianceAlertSeverity.MEDIUM,
                state=state,
                entity_type="StateReport",
                metric_value=float((timezone.localdate() - latest.reporting_period_end).days) if latest else None,
                threshold_value=float(THRESHOLDS["report_overdue_days"]),
            ))
        return cls._tally(results)

    @classmethod
    def _detect_unusual_certificate_pattern(cls):
        window = timezone.now() - timezone.timedelta(hours=24)
        threshold = THRESHOLDS["unusual_cert_per_facility_24h"]
        rows = (
            Certificate.objects.filter(created_at__gte=window)
            .values("facility_id", "facility__facility_name", "issuing_state_id")
            .annotate(total=Count("id"))
            .filter(total__gte=threshold)
        )
        results = []
        for row in rows:
            results.append(cls._upsert(
                alert_type=ComplianceAlertType.UNUSUAL_CERTIFICATE_PATTERN,
                dedupe_key=f"unusual_certificate_pattern:{row['facility_id']}",
                title=f"Unusual certificate volume at {row['facility__facility_name'] or 'facility'}",
                description=f"{row['total']} certificates generated in the last 24 hours (threshold {threshold}).",
                severity=ComplianceAlertSeverity.HIGH,
                state_id=row["issuing_state_id"],
                entity_type="MedicalFacility",
                entity_id=str(row["facility_id"]),
                metric_value=float(row["total"]),
                threshold_value=float(threshold),
            ))
        return cls._tally(results)

    @classmethod
    def _detect_duplicate_active_certificates(cls):
        today = timezone.localdate()
        rows = (
            Certificate.objects.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today)
            .values("food_handler_id", "food_handler__full_name", "food_handler__nin")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
        )
        results = []
        for row in rows:
            results.append(cls._upsert(
                alert_type=ComplianceAlertType.DUPLICATE_ACTIVE_CERTIFICATES,
                dedupe_key=f"duplicate_active_certificates:{row['food_handler_id']}",
                title=f"Duplicate active certificates for {row['food_handler__full_name'] or 'food handler'}",
                description=f"{row['total']} active certificates found for the same food handler (NIN {row['food_handler__nin'] or 'unknown'}).",
                severity=ComplianceAlertSeverity.CRITICAL,
                entity_type="FoodHandlerProfile",
                entity_id=str(row["food_handler_id"]),
                metric_value=float(row["total"]),
                threshold_value=1.0,
                metadata={"nin": row["food_handler__nin"] or ""},
            ))
        return cls._tally(results)

    @classmethod
    def _detect_high_facility_suspension(cls):
        rate_threshold = THRESHOLDS["high_facility_suspension_rate"]
        min_suspended = THRESHOLDS["high_facility_suspension_min"]
        rows = (
            MedicalFacility.objects.values("state_id", "state__name")
            .annotate(
                total=Count("id"),
                suspended=Count("id", filter=Q(accreditation_status=AccreditationStatus.SUSPENDED)),
            )
            .filter(suspended__gte=min_suspended)
        )
        results = []
        for row in rows:
            total = row["total"] or 1
            rate = row["suspended"] / total
            if rate < rate_threshold:
                continue
            results.append(cls._upsert(
                alert_type=ComplianceAlertType.HIGH_FACILITY_SUSPENSION,
                dedupe_key=f"high_facility_suspension:{row['state_id']}",
                title=f"High facility suspension rate in {row['state__name'] or 'Unknown'}",
                description=f"{row['suspended']} of {total} facilities suspended ({rate:.0%}).",
                severity=ComplianceAlertSeverity.HIGH,
                state_id=row["state_id"],
                entity_type="State",
                entity_id=str(row["state_id"]) if row["state_id"] else "",
                metric_value=round(rate, 4),
                threshold_value=rate_threshold,
            ))
        return cls._tally(results)

    @classmethod
    def _detect_high_pending_lab_results(cls):
        threshold = THRESHOLDS["high_pending_lab_results"]
        rows = (
            LabTest.objects.filter(status__in=PENDING_LAB_STATUSES)
            .values("assessment__facility_id", "assessment__facility__facility_name", "assessment__facility__state_id")
            .annotate(total=Count("id"))
            .filter(total__gte=threshold)
        )
        results = []
        for row in rows:
            facility_id = row["assessment__facility_id"]
            results.append(cls._upsert(
                alert_type=ComplianceAlertType.HIGH_PENDING_LAB_RESULTS,
                dedupe_key=f"high_pending_lab_results:{facility_id}",
                title=f"High pending lab results at {row['assessment__facility__facility_name'] or 'facility'}",
                description=f"{row['total']} lab tests are still pending (threshold {threshold}).",
                severity=ComplianceAlertSeverity.MEDIUM,
                state_id=row["assessment__facility__state_id"],
                entity_type="MedicalFacility",
                entity_id=str(facility_id) if facility_id else "",
                metric_value=float(row["total"]),
                threshold_value=float(threshold),
            ))
        return cls._tally(results)

    @classmethod
    def _detect_high_expired_certificates(cls):
        today = timezone.localdate()
        threshold = THRESHOLDS["high_expired_certificates"]
        rows = (
            Certificate.objects.filter(Q(status=CertificateStatus.EXPIRED) | Q(expiry_date__lt=today))
            .values("issuing_state_id", "issuing_state__name")
            .annotate(total=Count("id"))
            .filter(total__gte=threshold)
        )
        results = []
        for row in rows:
            results.append(cls._upsert(
                alert_type=ComplianceAlertType.HIGH_EXPIRED_CERTIFICATES,
                dedupe_key=f"high_expired_certificates:{row['issuing_state_id']}",
                title=f"High expired certificate count in {row['issuing_state__name'] or 'Unknown'}",
                description=f"{row['total']} certificates are expired (threshold {threshold}).",
                severity=ComplianceAlertSeverity.MEDIUM,
                state_id=row["issuing_state_id"],
                entity_type="State",
                entity_id=str(row["issuing_state_id"]) if row["issuing_state_id"] else "",
                metric_value=float(row["total"]),
                threshold_value=float(threshold),
            ))
        return cls._tally(results)

    @classmethod
    def _detect_verification_failures(cls):
        window = timezone.now() - timezone.timedelta(hours=THRESHOLDS["verification_failure_window_hours"])
        threshold = THRESHOLDS["verification_failure_count"]
        count = CertificateVerificationLog.objects.filter(
            created_at__gte=window,
            result__in=[VerificationResult.INVALID, VerificationResult.NOT_FOUND],
        ).count()
        if count < threshold:
            return 0, 0
        created = cls._upsert(
            alert_type=ComplianceAlertType.CERTIFICATE_VERIFICATION_FAILURE,
            dedupe_key="certificate_verification_failure:national",
            title="Certificate verification failure spike",
            description=f"{count} invalid/not-found verification attempts in the last {THRESHOLDS['verification_failure_window_hours']}h (threshold {threshold}).",
            severity=ComplianceAlertSeverity.HIGH,
            entity_type="CertificateVerificationLog",
            metric_value=float(count),
            threshold_value=float(threshold),
        )
        return cls._tally([created])
