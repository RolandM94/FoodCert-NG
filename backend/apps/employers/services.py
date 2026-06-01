from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.utils import timezone

from rest_framework.exceptions import PermissionDenied as DrfPermissionDenied, ValidationError as DrfValidationError

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import Certificate, CertificateStatus
from apps.employers.models import Employer, ComplianceStatus, SubscriptionStatus
from apps.food_handlers.models import FoodHandlerProfile, FoodHandlerStatus
from apps.illness.models import IllnessReport
from apps.inspections.models import Inspection, InspectionStatus
from apps.notifications.models import Notification
from apps.organizations.models import Organization, OrganizationType
from apps.organizations.models import OrganizationUnit, OrganizationUnitType
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus, VaccineType


class EmployerService:
    @classmethod
    def register_business(cls, *, actor, organization=None, **data):
        if actor.role != UserRole.EMPLOYER:
            raise DrfPermissionDenied("Only employer users can register a business.")

        if Employer.objects.filter(user=actor).exists():
            raise DrfPermissionDenied("Employer profile already exists.")

        if not organization:
            organization = Organization.objects.create(
                name=data.get("business_name", f"Business of {actor.email}"),
                organization_type=OrganizationType.EMPLOYER,
                state=data.get("state"),
                lga=data.get("lga"),
                address=data.get("address", ""),
                phone=data.get("contact_person_phone", ""),
                email=data.get("contact_person_email", actor.email),
            )
        elif organization.organization_type != OrganizationType.EMPLOYER:
            raise DrfValidationError("Organization must be an employer type.")

        if data.get("business_name") and not organization.name.startswith(data["business_name"]):
            organization.name = data["business_name"]
            organization.save(update_fields=["name"])

        employer = Employer.objects.create(
            user=actor,
            organization=organization,
            business_name=data.get("business_name", organization.name),
            business_registration_number=data.get("business_registration_number", ""),
            business_type=data.get("business_type", ""),
            establishment_category=data.get("establishment_category"),
            contact_person_name=data.get("contact_person_name", actor.get_full_name() or actor.username),
            contact_person_phone=data.get("contact_person_phone", actor.phone or ""),
            contact_person_email=data.get("contact_person_email", actor.email),
            address=data.get("address", organization.address or ""),
            state=data.get("state", organization.state),
            lga=data.get("lga", organization.lga),
            ward=data.get("ward", ""),
            number_of_food_handlers=data.get("number_of_food_handlers", 0),
            compliance_status=ComplianceStatus.UNDER_REVIEW,
            subscription_status=SubscriptionStatus.NEVER_SUBSCRIBED,
        )

        actor.organization = organization
        actor.save(update_fields=["organization", "updated_at"])

        log_action(action=AuditAction.CREATE, actor=actor, target=employer, metadata={"event": "employer_registered"})
        return employer

    @classmethod
    def update_profile(cls, *, employer, actor, **data):
        if actor.role == UserRole.EMPLOYER and employer.user_id != actor.id:
            raise DrfPermissionDenied("You can only update your own employer profile.")

        allowed_fields = {
            "business_name", "business_registration_number", "business_type",
            "establishment_category", "contact_person_name", "contact_person_phone",
            "contact_person_email", "address", "state", "lga", "ward",
            "number_of_food_handlers",
        }
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        for field, value in updates.items():
            setattr(employer, field, value)
        employer.save()

        if updates.get("business_name") and employer.organization:
            employer.organization.name = updates["business_name"]
            employer.organization.save(update_fields=["name", "updated_at"])

        log_action(action=AuditAction.UPDATE, actor=actor, target=employer, metadata={"event": "employer_profile_updated"})
        return employer

    @classmethod
    def get_for_user(cls, user):
        if hasattr(user, "employer"):
            return user.employer
        raise DrfPermissionDenied("No employer profile found for this user.")


class EmployerDashboardService:
    @classmethod
    def _branch_id(cls, *, employer, actor, branch_id=None):
        if getattr(actor, "role", None) == UserRole.EMPLOYER and getattr(actor, "unit_restricted", False) and actor.unit_id:
            return actor.unit_id
        if not branch_id:
            return None
        if not OrganizationUnit.objects.filter(
            id=branch_id,
            organization=employer.organization,
            unit_type=OrganizationUnitType.BRANCH,
        ).exists():
            raise DrfValidationError("Branch must belong to this employer organization.")
        return branch_id

    @classmethod
    def _handlers(cls, *, employer, actor, branch_id=None):
        scoped_branch = cls._branch_id(employer=employer, actor=actor, branch_id=branch_id)
        queryset = FoodHandlerProfile.objects.select_related("business_branch").filter(employer=employer)
        if scoped_branch:
            queryset = queryset.filter(business_branch_id=scoped_branch)
        return queryset, scoped_branch

    @classmethod
    def dashboard(cls, *, employer, actor, branch_id=None):
        handlers, scoped_branch = cls._handlers(employer=employer, actor=actor, branch_id=branch_id)
        today = timezone.localdate()
        total_handlers = handlers.count()
        handler_ids = list(handlers.values_list("id", flat=True))
        certificates = Certificate.objects.filter(food_handler_id__in=handler_ids)
        valid_certificates = certificates.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today).values("food_handler_id").distinct().count()
        expiring_soon = certificates.filter(
            status=CertificateStatus.ACTIVE,
            expiry_date__gte=today,
            expiry_date__lte=today + timezone.timedelta(days=30),
        ).values("food_handler_id").distinct().count()
        expiring_7d = certificates.filter(
            status=CertificateStatus.ACTIVE,
            expiry_date__gte=today,
            expiry_date__lte=today + timezone.timedelta(days=7),
        ).values("food_handler_id").distinct().count()
        expired = certificates.filter(Q(status=CertificateStatus.EXPIRED) | Q(status=CertificateStatus.ACTIVE, expiry_date__lt=today)).values("food_handler_id").distinct().count()
        vaccination_due = VaccinationRecord.objects.filter(
            food_handler_id__in=handler_ids,
            status__in=[VaccinationStatus.EXPIRED, VaccinationStatus.MISSING, VaccinationStatus.SECOND_DOSE_DUE],
        ).values("food_handler_id").distinct().count()
        open_inspections = Inspection.objects.select_related("branch").filter(employer=employer).exclude(status=InspectionStatus.CLOSED)
        if scoped_branch:
            open_inspections = open_inspections.filter(branch_id=scoped_branch)
        branches = OrganizationUnit.objects.filter(
            organization=employer.organization,
            unit_type=OrganizationUnitType.BRANCH,
            is_active=True,
        )
        if scoped_branch:
            branches = branches.filter(id=scoped_branch)
        compliance_percentage = round((valid_certificates / total_handlers) * 100, 1) if total_handlers else 0

        cards = {
            "total_handlers": total_handlers,
            "fit": handlers.filter(current_status=FoodHandlerStatus.FIT).count(),
            "certification_pending": handlers.filter(current_status__in=[FoodHandlerStatus.PROFILE_INCOMPLETE, FoodHandlerStatus.NIN_PENDING, FoodHandlerStatus.CERTIFICATION_PENDING]).count(),
            "expired_certificates": expired,
            "expiring_soon": expiring_soon,
            "expiring_7d": expiring_7d,
            "temporarily_not_fit": handlers.filter(current_status=FoodHandlerStatus.TEMPORARILY_NOT_FIT).count(),
            "excluded": handlers.filter(current_status__in=[FoodHandlerStatus.TEMPORARILY_EXCLUDED, FoodHandlerStatus.EXCLUDED]).count(),
            "vaccination_due": vaccination_due,
            "active_branches": branches.count(),
            "open_inspections": open_inspections.count(),
            "subscription_status": employer.subscription_status,
            "compliance_percentage": compliance_percentage,
        }

        recent_activity = cls._recent_activity(employer=employer, actor=actor, scoped_branch=scoped_branch)
        return {
            "employer": {
                "id": str(employer.id),
                "business_name": employer.business_name,
                "organization": str(employer.organization_id) if employer.organization_id else None,
                "subscription_status": employer.subscription_status,
            },
            "scope": cls._scope_payload(scoped_branch),
            "cards": cards,
            "charts": cls.compliance_summary(employer=employer, actor=actor, branch_id=scoped_branch),
            "open_inspection_notices": [
                {
                    "id": str(inspection.id),
                    "branch_name": inspection.branch.name if inspection.branch else "Head office",
                    "inspection_date": inspection.inspection_date.isoformat(),
                    "status": inspection.status,
                    "enforcement_action": inspection.enforcement_action,
                    "findings_summary": inspection.findings[:180],
                }
                for inspection in open_inspections.order_by("-inspection_date")[:5]
            ],
            "recent_activity": recent_activity,
        }

    @classmethod
    def _scope_payload(cls, scoped_branch):
        if not scoped_branch:
            return {"branch": None, "branch_name": None, "locked": False}
        branch = OrganizationUnit.objects.filter(id=scoped_branch).first()
        return {
            "branch": str(scoped_branch),
            "branch_name": branch.name if branch else None,
            "locked": True,
        }

    @classmethod
    def _recent_activity(cls, *, employer, actor, scoped_branch=None):
        rows = []
        notifications = Notification.objects.filter(
            recipient__organization=employer.organization,
        ).order_by("-created_at")[:6]
        for item in notifications:
            rows.append({
                "id": str(item.id),
                "kind": "notification",
                "title": item.title,
                "description": item.message[:160],
                "created_at": item.created_at.isoformat(),
            })
        inspections = Inspection.objects.filter(employer=employer)
        if scoped_branch:
            inspections = inspections.filter(branch_id=scoped_branch)
        for inspection in inspections.order_by("-created_at")[:4]:
            rows.append({
                "id": str(inspection.id),
                "kind": "inspection",
                "title": f"Inspection {inspection.get_status_display()}",
                "description": inspection.findings[:160] or "Inspection activity recorded.",
                "created_at": inspection.created_at.isoformat(),
                "status": inspection.status,
            })
        return sorted(rows, key=lambda row: row["created_at"], reverse=True)[:8]

    @classmethod
    def compliance_summary(cls, *, employer, actor, branch_id=None):
        handlers, scoped_branch = cls._handlers(employer=employer, actor=actor, branch_id=branch_id)
        today = timezone.localdate()
        handler_ids = list(handlers.values_list("id", flat=True))
        branches = OrganizationUnit.objects.filter(
            organization=employer.organization,
            unit_type=OrganizationUnitType.BRANCH,
            is_active=True,
        ).order_by("name")
        if scoped_branch:
            branches = branches.filter(id=scoped_branch)

        branch_breakdown = []
        for branch in branches:
            branch_handlers = handlers.filter(business_branch=branch)
            total = branch_handlers.count()
            branch_ids = list(branch_handlers.values_list("id", flat=True))
            certified = Certificate.objects.filter(food_handler_id__in=branch_ids, status=CertificateStatus.ACTIVE, expiry_date__gte=today).values("food_handler_id").distinct().count()
            branch_breakdown.append({
                "branch": str(branch.id),
                "branch_name": branch.name,
                "total_handlers": total,
                "certified_handlers": certified,
                "compliance_percentage": round((certified / total) * 100, 1) if total else 0,
            })

        cert_rows = Certificate.objects.filter(food_handler_id__in=handler_ids).values("status").annotate(count=Count("id")).order_by("status")
        certificate_status_distribution = [{"status": row["status"], "count": row["count"]} for row in cert_rows]
        expired_count = Certificate.objects.filter(food_handler_id__in=handler_ids, status=CertificateStatus.ACTIVE, expiry_date__lt=today).count()
        if expired_count:
            certificate_status_distribution.append({"status": CertificateStatus.EXPIRED, "count": expired_count})

        vaccination_coverage_summary = [
            {
                "vaccine_type": vaccine_type,
                "valid": VaccinationRecord.objects.filter(food_handler_id__in=handler_ids, vaccine_type=vaccine_type, status=VaccinationStatus.VALID).values("food_handler_id").distinct().count(),
                "expired": VaccinationRecord.objects.filter(food_handler_id__in=handler_ids, vaccine_type=vaccine_type, status=VaccinationStatus.EXPIRED).values("food_handler_id").distinct().count(),
                "due": VaccinationRecord.objects.filter(food_handler_id__in=handler_ids, vaccine_type=vaccine_type, status=VaccinationStatus.SECOND_DOSE_DUE).values("food_handler_id").distinct().count(),
                "missing": max(handlers.count() - VaccinationRecord.objects.filter(food_handler_id__in=handler_ids, vaccine_type=vaccine_type).values("food_handler_id").distinct().count(), 0),
            }
            for vaccine_type in [VaccineType.TYPHOID, VaccineType.HEPATITIS_A]
        ]

        expiring_certificates_timeline = []
        for days, label in [(7, "Next 7 days"), (30, "Next 30 days"), (60, "Next 60 days"), (90, "Next 90 days")]:
            expiring_certificates_timeline.append({
                "label": label,
                "count": Certificate.objects.filter(
                    food_handler_id__in=handler_ids,
                    status=CertificateStatus.ACTIVE,
                    expiry_date__gte=today,
                    expiry_date__lte=today + timezone.timedelta(days=days),
                ).count(),
            })

        illness_reports_trend = []
        for days, label in [(7, "7 days"), (30, "30 days"), (90, "90 days")]:
            illness_reports_trend.append({
                "label": label,
                "count": IllnessReport.objects.filter(
                    employer=employer,
                    food_handler_id__in=handler_ids,
                    created_at__gte=timezone.now() - timezone.timedelta(days=days),
                ).count(),
            })

        return {
            "branch_breakdown": branch_breakdown,
            "certificate_status_distribution": certificate_status_distribution,
            "vaccination_coverage_summary": vaccination_coverage_summary,
            "expiring_certificates_timeline": expiring_certificates_timeline,
            "illness_reports_trend": illness_reports_trend,
        }

    @classmethod
    def notifications(cls, *, employer, actor):
        queryset = Notification.objects.filter(
            recipient__organization=employer.organization,
        ).select_related("recipient").order_by("-created_at")
        rows = [
            {
                "id": str(item.id),
                "recipient_name": item.recipient.get_full_name() or item.recipient.email,
                "category": item.category,
                "title": item.title,
                "message": item.message,
                "created_at": item.created_at.isoformat(),
                "read_at": item.read_at.isoformat() if item.read_at else None,
            }
            for item in queryset[:50]
        ]
        return {
            "unread_count": queryset.filter(is_read=False).count(),
            "notifications": rows,
        }
