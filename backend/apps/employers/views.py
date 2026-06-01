from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import FileResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import EmployerStaffRole, UserInvite, UserRole
from apps.accounts.permissions import IsActiveUser
from apps.accounts.serializers import InviteUserSerializer, UserAdminSerializer
from apps.accounts.services import InviteService
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.employers.models import Employer, SubscriptionStatus as EmployerSubscriptionStatus
from apps.employers.permissions import IsEmployerOwner, IsEmployerOrRegulator, is_branch_manager
from apps.employers.serializers import (
    EmployerDashboardQuerySerializer,
    EmployerInviteCreateSerializer,
    EmployerInviteSerializer,
    EmployerSerializer,
    EmployerSettingsSerializer,
    EmployerUserSerializer,
    EmployerUserUpdateSerializer,
)
from apps.employers.services import EmployerDashboardService, EmployerService
from apps.food_handlers.models import FoodHandlerProfile
from apps.food_handlers.serializers import (
    EmployerFoodHandlerListSerializer,
    FoodHandlerBranchAssignmentSerializer,
)
from apps.certificates.models import Certificate, CertificateStatus
from apps.certificates.services import CertificateService
from apps.illness.models import IllnessReport
from apps.illness.services import IllnessService
from apps.inspections.models import Inspection
from apps.inspections.serializers import InspectionResponseCreateSerializer, InspectionResponseSerializer
from apps.inspections.services import InspectionService
from apps.payments.models import PaymentTransaction
from apps.payments.serializers import PaymentTransactionSerializer
from apps.payments.services import PaymentService
from apps.reports.models import ReportType
from apps.reports.serializers import GeneratedReportSerializer
from apps.reports.services import EmployerReportService
from apps.notifications.models import Notification, NotificationCategory
from apps.subscriptions.serializers import (
    EmployerEntitlementSerializer,
    EmployerInvoiceSerializer,
    EmployerSubscriptionCancelSerializer,
    EmployerSubscriptionChangePlanSerializer,
    EmployerSubscriptionCheckoutSerializer,
    EmployerSubscriptionSerializer,
)
from apps.subscriptions.services import EmployerInvoiceService, EmployerSubscriptionService
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus, VaccineType

User = get_user_model()


class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.select_related("user", "organization", "state", "lga").order_by("-created_at")
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        queryset = self.queryset
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(state=user.state)
        if user.role == UserRole.EMPLOYER:
            base = queryset.filter(user=user)
            if user.organization_id and not base.exists():
                base = queryset.filter(organization=user.organization)
            return base
        if user.organization_id:
            return queryset.filter(organization=user.organization)
        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        profile = EmployerService.register_business(
            actor=user,
            **serializer.validated_data,
        )
        serializer.instance = profile

    def perform_update(self, serializer):
        profile = self.get_object()
        user = self.request.user
        if user.role == UserRole.EMPLOYER and profile.user_id != user.id:
            raise PermissionDenied("Only the business owner can edit the employer profile.")
        updated = EmployerService.update_profile(
            employer=profile,
            actor=user,
            **serializer.validated_data,
        )
        serializer.instance = updated

    @action(detail=False, methods=["get"], url_path="me", permission_classes=[IsAuthenticated, IsActiveUser, IsEmployerOwner])
    def me(self, request):
        employer = EmployerService.get_for_user(request.user)
        return Response(EmployerSerializer(employer).data)

    @action(detail=True, methods=["get"], url_path="food-handlers")
    def food_handlers(self, request, pk=None):
        employer = self.get_object()
        user = request.user
        self._ensure_can_view_employer_health_data(employer, user)

        queryset = FoodHandlerProfile.objects.select_related(
            "business_branch", "employer", "state"
        ).prefetch_related(
            "certificates", "vaccinations"
        ).filter(employer=employer).order_by("full_name")

        if is_branch_manager(user) and user.unit_id:
            queryset = queryset.filter(business_branch=user.unit)

        branch_id = request.query_params.get("branch")
        if branch_id:
            queryset = queryset.filter(business_branch_id=branch_id)

        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(food_handler_category=category)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(full_name__icontains=search)

        serializer = EmployerFoodHandlerListSerializer(queryset, many=True)
        rows = list(serializer.data)

        fitness_status = request.query_params.get("fitness_status")
        if fitness_status:
            rows = [row for row in rows if row.get("fitness_status") == fitness_status]

        certificate_status = request.query_params.get("certificate_status")
        if certificate_status:
            rows = [row for row in rows if row.get("certificate_status") == certificate_status]

        expiry_window = request.query_params.get("expiry_window")
        if expiry_window in {"7", "30", "90"}:
            today = timezone.localdate()
            cutoff = today + timedelta(days=int(expiry_window))
            rows = [
                row for row in rows
                if row.get("certificate_expiry_date")
                and today <= date.fromisoformat(row["certificate_expiry_date"]) <= cutoff
            ]

        return Response(rows)

    @extend_schema(request=InviteUserSerializer, responses={201: UserAdminSerializer})
    @action(detail=True, methods=["post"], url_path="invite-food-handler")
    def invite_food_handler(self, request, pk=None):
        employer = self.get_object()
        user = request.user
        if user.role == UserRole.EMPLOYER and employer.organization_id != user.organization_id:
            raise PermissionDenied("You can only invite food handlers for your own business.")
        if user.role == UserRole.STATE_ADMIN and employer.state_id != user.state_id:
            raise PermissionDenied("State admins can only invite users in their state.")
        if is_branch_manager(user) and user.unit_id:
            request.data["unit"] = str(user.unit_id)
        payload = {
            **request.data,
            "role": UserRole.FOOD_HANDLER,
            "organization": str(employer.organization_id) if employer.organization_id else None,
            "state": str(employer.state_id),
        }
        serializer = InviteUserSerializer(data=payload, context={"request": request})
        serializer.is_valid(raise_exception=True)
        invited = serializer.save()
        log_action(action=AuditAction.CREATE, actor=user, target=invited, metadata={"event": "employer_food_handler_invite", "employer_id": str(employer.id)})
        return Response(UserAdminSerializer(invited).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="food-handlers/bulk-upload")
    def bulk_upload_food_handlers(self, request, pk=None):
        employer = self.get_object()
        user = request.user
        if is_branch_manager(user) and user.unit_id:
            default_branch = str(user.unit_id)
        else:
            default_branch = request.data.get("branch", "")
        rows = request.data.get("rows", [])
        if not isinstance(rows, list) or not rows:
            raise ValidationError("Provide a 'rows' list with handler entries.")
        created = []
        errors = []
        for i, row in enumerate(rows):
            if not row.get("full_name") or not row.get("phone"):
                errors.append({"row": i, "error": "full_name and phone are required."})
                continue
            try:
                invite_data = {
                    "username": row.get("username") or (row.get("email") or f"handler-{row['phone']}").split("@")[0],
                    "email": row.get("email", f"handler-{row['phone']}@placeholder.ng"),
                    "phone": row["phone"],
                    "role": UserRole.FOOD_HANDLER,
                    "organization": str(employer.organization_id) if employer.organization_id else None,
                    "state": str(employer.state_id),
                    "unit": row.get("branch", default_branch) or None,
                }
                invite_serializer = InviteUserSerializer(data=invite_data, context={"request": request})
                invite_serializer.is_valid(raise_exception=False)
                if invite_serializer.errors:
                    errors.append({"row": i, "error": invite_serializer.errors})
                else:
                    invited = invite_serializer.save()
                    created.append({"row": i, "user_id": str(invited.id), "email": invited.email})
            except Exception as e:
                errors.append({"row": i, "error": str(e)})
        log_action(action=AuditAction.CREATE, actor=user, target=employer, metadata={"event": "bulk_invite", "created": len(created), "errors": len(errors)})
        return Response({"created": created, "errors": errors}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="food-handlers/search")
    def search_food_handlers(self, request, pk=None):
        employer = self.get_object()
        query = request.query_params.get("q", "")
        if len(query) < 3:
            return Response([])
        from django.db.models import Q
        results = FoodHandlerProfile.objects.filter(
            Q(phone__icontains=query) | Q(full_name__icontains=query) | Q(system_identifier__icontains=query) | Q(email__icontains=query),
        ).exclude(employer=employer)[:10]
        return Response(EmployerFoodHandlerListSerializer(results, many=True).data)

    @action(detail=True, methods=["post"], url_path="food-handlers/(?P<fh_id>[^/.]+)/link")
    def link_food_handler(self, request, pk=None, fh_id=None):
        employer = self.get_object()
        user = request.user
        fh = FoodHandlerProfile.objects.filter(id=fh_id, employer__isnull=True).first()
        if not fh:
            raise ValidationError("Food handler not found or already linked to an employer.")
        fh.employer = employer
        if request.data.get("branch"):
            fh.business_branch_id = request.data["branch"]
        elif is_branch_manager(user) and user.unit_id:
            fh.business_branch = user.unit
        fh.save(update_fields=["employer", "business_branch", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=user, target=fh, metadata={"event": "link_to_employer", "employer_id": str(employer.id)})
        return Response(EmployerFoodHandlerListSerializer(fh).data)

    @action(detail=True, methods=["patch"], url_path="food-handlers/(?P<fh_id>[^/.]+)/branch")
    def reassign_branch(self, request, pk=None, fh_id=None):
        employer = self.get_object()
        user = request.user
        if is_branch_manager(user):
            raise PermissionDenied("Branch managers cannot reassign food handlers between branches.")
        fh = FoodHandlerProfile.objects.filter(id=fh_id, employer=employer).first()
        if not fh:
            raise ValidationError("Food handler not found under this employer.")
        serializer = FoodHandlerBranchAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fh.business_branch = serializer.validated_data.get("business_branch")
        fh.save(update_fields=["business_branch", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=user, target=fh, metadata={"event": "branch_reassign", "new_branch": str(fh.business_branch_id)})
        return Response(EmployerFoodHandlerListSerializer(fh).data)

    @action(detail=True, methods=["get"], url_path="certificates")
    def certificates(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        queryset = self._employer_certificate_queryset(employer, request.user).order_by("-issue_date")
        today = timezone.localdate()

        branch = request.query_params.get("branch")
        if branch:
            queryset = queryset.filter(food_handler__business_branch_id=branch)

        status_filter = request.query_params.get("status")
        if status_filter:
            if status_filter == "expired":
                queryset = queryset.filter(status=CertificateStatus.ACTIVE, expiry_date__lt=today)
            else:
                queryset = queryset.filter(status=status_filter)

        expiry_window = request.query_params.get("expiry_window")
        if expiry_window == "expired":
            queryset = queryset.filter(expiry_date__lt=today)
        elif expiry_window:
            try:
                days = int(expiry_window)
                queryset = queryset.filter(expiry_date__gte=today, expiry_date__lte=today + timezone.timedelta(days=days))
            except ValueError:
                raise ValidationError("Expiry window must be a number of days or 'expired'.")

        all_certs = self._employer_certificate_queryset(employer, request.user)
        if branch:
            all_certs = all_certs.filter(food_handler__business_branch_id=branch)

        metrics = {
            "total": all_certs.count(),
            "active": all_certs.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today).count(),
            "expired": all_certs.filter(expiry_date__lt=today, status=CertificateStatus.ACTIVE).count(),
            "expiring_30d": all_certs.filter(expiry_date__lte=today + timezone.timedelta(days=30), expiry_date__gte=today, status=CertificateStatus.ACTIVE).count(),
            "expiring_7d": all_certs.filter(expiry_date__lte=today + timezone.timedelta(days=7), expiry_date__gte=today, status=CertificateStatus.ACTIVE).count(),
            "revoked": all_certs.filter(status=CertificateStatus.REVOKED).count(),
        }

        data = {
            "metrics": metrics,
            "certificates": [
                {
                    "id": str(c.id),
                    "certificate_number": c.certificate_number,
                    "food_handler_name": c.food_handler.full_name,
                    "branch_name": c.food_handler.business_branch.name if c.food_handler.business_branch else None,
                    "facility_name": c.facility.facility_name,
                    "issuing_state_name": c.issuing_state.name,
                    "issue_date": c.issue_date.isoformat(),
                    "expiry_date": c.expiry_date.isoformat(),
                    "status": c.status,
                    "effective_status": c.effective_status,
                    "verification_url": c.verification_url,
                    "can_download": bool(c.pdf_url),
                }
                for c in queryset[:200]
            ],
        }
        return Response(data)

    def _employer_certificate_queryset(self, employer, user):
        queryset = Certificate.objects.select_related(
            "food_handler",
            "food_handler__business_branch",
            "facility",
            "issuing_state",
        ).filter(food_handler__employer=employer)
        if user.unit_restricted and user.unit_id:
            queryset = queryset.filter(food_handler__business_branch_id=user.unit_id)
        return queryset

    def _get_employer_certificate(self, employer, user, certificate_id):
        certificate = self._employer_certificate_queryset(employer, user).filter(id=certificate_id).first()
        if not certificate:
            raise ValidationError("Certificate not found under this employer.")
        return certificate

    @action(detail=True, methods=["get"], url_path=r"certificates/(?P<certificate_id>[^/.]+)")
    def certificate_detail(self, request, pk=None, certificate_id=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        c = self._get_employer_certificate(employer, request.user, certificate_id)
        return Response({
            "id": str(c.id),
            "certificate_number": c.certificate_number,
            "food_handler_name": c.food_handler.full_name,
            "branch_name": c.food_handler.business_branch.name if c.food_handler.business_branch else None,
            "facility_name": c.facility.facility_name,
            "issuing_state_name": c.issuing_state.name,
            "issue_date": c.issue_date.isoformat(),
            "expiry_date": c.expiry_date.isoformat(),
            "status": c.status,
            "effective_status": c.effective_status,
            "verification_url": c.verification_url,
            "can_download": bool(c.pdf_url),
        })

    @action(detail=True, methods=["get"], url_path=r"certificates/(?P<certificate_id>[^/.]+)/download")
    def certificate_download(self, request, pk=None, certificate_id=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        certificate = self._get_employer_certificate(employer, request.user, certificate_id)
        certificate.pdf_url = CertificateService.write_pdf(certificate=certificate)
        certificate.save(update_fields=["pdf_url", "updated_at"])
        media_prefix = "http://localhost:8000/media/"
        relative_path = certificate.pdf_url.replace(media_prefix, "")
        file_path = str(settings.MEDIA_ROOT / relative_path)
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=request.user, target=certificate, metadata={"event": "employer_certificate_download"})
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=f"{certificate.certificate_number}.pdf")

    @action(detail=True, methods=["post"], url_path=r"certificates/(?P<certificate_id>[^/.]+)/send-renewal-reminder")
    def certificate_renewal_reminder(self, request, pk=None, certificate_id=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        certificate = self._get_employer_certificate(employer, request.user, certificate_id)
        if certificate.food_handler.user_id:
            Notification.objects.create(
                recipient=certificate.food_handler.user,
                category=NotificationCategory.RENEWAL,
                title="Certificate renewal reminder",
                message=f"{employer.business_name} sent a reminder to renew your FoodCert NG certificate.",
            )
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=request.user, target=certificate, metadata={"event": "employer_certificate_renewal_reminder_sent"})
        return Response({"status": "sent", "certificate_id": str(certificate.id)})

    @action(detail=True, methods=["get"], url_path="vaccinations")
    def vaccinations(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        handlers = FoodHandlerProfile.objects.filter(employer=employer).prefetch_related("vaccinations")
        branch = request.query_params.get("branch")
        if branch:
            handlers = handlers.filter(business_branch_id=branch)

        total = handlers.count()
        typhoid_valid = sum(1 for h in handlers if h.vaccinations.filter(vaccine_type=VaccineType.TYPHOID, status=VaccinationStatus.VALID).exists())
        typhoid_expired = sum(1 for h in handlers if h.vaccinations.filter(vaccine_type=VaccineType.TYPHOID, status=VaccinationStatus.EXPIRED).exists())
        hepa_dose1 = sum(1 for h in handlers if h.vaccinations.filter(vaccine_type=VaccineType.HEPATITIS_A, dose_number=1).exists())
        hepa_complete = sum(1 for h in handlers if h.vaccinations.filter(vaccine_type=VaccineType.HEPATITIS_A, dose_number=2).exists())
        hepa_dose2_pending = sum(1 for h in handlers if h.vaccinations.filter(vaccine_type=VaccineType.HEPATITIS_A, dose_number=1, status=VaccinationStatus.SECOND_DOSE_DUE).exists())

        rows = []
        def compliance(record):
            return record.compliance_status if record else "due"

        for h in handlers.order_by("full_name")[:200]:
            typhoid = h.vaccinations.filter(vaccine_type=VaccineType.TYPHOID).order_by("-date_administered").first()
            hepa1 = h.vaccinations.filter(vaccine_type=VaccineType.HEPATITIS_A, dose_number=1).order_by("-date_administered").first()
            hepa2 = h.vaccinations.filter(vaccine_type=VaccineType.HEPATITIS_A, dose_number=2).order_by("-date_administered").first()
            rows.append({
                "food_handler_id": str(h.id),
                "food_handler_name": h.full_name,
                "branch_name": h.business_branch.name if h.business_branch else None,
                "typhoid_status": typhoid.status if typhoid else "not_recorded",
                "typhoid_compliance_status": compliance(typhoid),
                "typhoid_expiry_date": typhoid.expiry_date.isoformat() if typhoid and typhoid.expiry_date else None,
                "hepatitis_a_dose_1_date": hepa1.date_administered.isoformat() if hepa1 else None,
                "hepatitis_a_dose_2_date": hepa2.date_administered.isoformat() if hepa2 else None,
                "hepatitis_a_status": "complete" if hepa2 else ("dose_1_completed" if hepa1 else "not_recorded"),
                "hepatitis_a_compliance_status": "compliant" if hepa2 else compliance(hepa1),
                "next_due_date": (typhoid.expiry_date.isoformat() if typhoid and typhoid.status == VaccinationStatus.VALID and typhoid.expiry_date else (
                    hepa1.next_dose_date.isoformat() if hepa1 and hepa1.next_dose_date else None
                )),
            })

        return Response({
            "metrics": {
                "total_handlers": total,
                "typhoid_valid": typhoid_valid,
                "typhoid_expired": typhoid_expired,
                "typhoid_missing": total - typhoid_valid - typhoid_expired,
                "hepatitis_a_dose_1": hepa_dose1,
                "hepatitis_a_complete": hepa_complete,
                "hepatitis_a_dose_2_pending": hepa_dose2_pending,
                "hepatitis_a_missing": total - hepa_dose1,
            },
            "handlers": rows,
        })

    def _ensure_can_manage_billing(self, employer, user):
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        if user.role == UserRole.STATE_ADMIN and employer.state_id == user.state_id:
            return
        if (
            user.role == UserRole.EMPLOYER
            and employer.organization_id == user.organization_id
            and not is_branch_manager(user)
            and user.employer_staff_role != EmployerStaffRole.COMPLIANCE_OFFICER
        ):
            return
        raise PermissionDenied("You cannot access billing for this employer.")

    def _ensure_can_view_employer_health_data(self, employer, user):
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and employer.state_id == user.state_id:
            return
        if (
            user.role == UserRole.EMPLOYER
            and employer.organization_id == user.organization_id
            and user.employer_staff_role != EmployerStaffRole.FINANCE_USER
        ):
            return
        raise PermissionDenied("You cannot access food handler health data for this employer.")

    def _ensure_can_manage_employer_staff(self, employer, user):
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        if user.role == UserRole.STATE_ADMIN and employer.state_id == user.state_id:
            return
        if user.role == UserRole.EMPLOYER and employer.organization_id == user.organization_id and not is_branch_manager(user):
            return
        raise PermissionDenied("You cannot manage employer staff.")

    def _employer_staff_queryset(self, employer, request):
        queryset = User.objects.select_related("organization", "unit", "state").filter(
            organization=employer.organization,
            role=UserRole.EMPLOYER,
        ).order_by("first_name", "last_name", "email")
        user = request.user
        if is_branch_manager(user) and user.unit_id:
            queryset = queryset.filter(unit=user.unit, unit_restricted=True)
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        unit = request.query_params.get("unit")
        if unit:
            queryset = queryset.filter(unit_id=unit)
        staff_role = request.query_params.get("employer_staff_role")
        if staff_role == EmployerStaffRole.BRANCH_MANAGER:
            queryset = queryset.filter(unit__isnull=False, unit_restricted=True)
        elif staff_role in {EmployerStaffRole.EMPLOYER_ADMIN, EmployerStaffRole.COMPLIANCE_OFFICER, EmployerStaffRole.FINANCE_USER}:
            queryset = queryset.filter(employer_staff_role=staff_role)
        return queryset

    def _employer_billing_transactions(self, employer):
        return PaymentTransaction.objects.select_related("payer_user").filter(
            payer_type="employer",
            related_entity_type="employer_subscription",
            related_entity_id=employer.id,
        ).order_by("-created_at")

    @action(detail=True, methods=["get"], url_path="dashboard")
    def employer_dashboard(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        serializer = EmployerDashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(EmployerDashboardService.dashboard(
            employer=employer,
            actor=request.user,
            branch_id=serializer.validated_data.get("branch"),
        ))

    @action(detail=True, methods=["get"], url_path="compliance-summary")
    def employer_compliance_summary(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        serializer = EmployerDashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(EmployerDashboardService.compliance_summary(
            employer=employer,
            actor=request.user,
            branch_id=serializer.validated_data.get("branch"),
        ))

    @action(detail=True, methods=["get"], url_path="notifications")
    def employer_notifications(self, request, pk=None):
        employer = self.get_object()
        return Response(EmployerDashboardService.notifications(employer=employer, actor=request.user))

    @extend_schema(request=EmployerSettingsSerializer, responses=EmployerSettingsSerializer)
    @action(detail=True, methods=["get", "patch"], url_path="settings")
    def employer_settings(self, request, pk=None):
        employer = self.get_object()
        if request.method == "GET":
            return Response(EmployerSettingsSerializer(employer).data)
        if is_branch_manager(request.user):
            raise PermissionDenied("Branch managers cannot update organization-wide settings.")
        serializer = EmployerSettingsSerializer(employer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_action(action=AuditAction.UPDATE, actor=request.user, target=employer, metadata={"event": "employer_settings_updated"})
        return Response(serializer.data)

    @extend_schema(request=EmployerSubscriptionCheckoutSerializer, responses={201: EmployerSubscriptionSerializer})
    @action(detail=True, methods=["post"], url_path="subscription/checkout")
    def subscription_checkout(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_manage_billing(employer, request.user)
        serializer = EmployerSubscriptionCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.validated_data["plan"]
        billing_cycle = serializer.validated_data["billing_cycle"]
        transaction_obj = PaymentService.initiate_subscription_payment(
            payer_user=request.user,
            employer=employer,
            plan=plan,
            billing_cycle=billing_cycle,
        )
        invoice = EmployerInvoiceService.create_for_subscription_checkout(
            employer=employer,
            plan=plan,
            billing_cycle=billing_cycle,
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        transaction_obj = PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=request.user)
        subscription = EmployerSubscriptionService.activate(
            employer=employer,
            plan=plan,
            billing_cycle=billing_cycle,
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        EmployerInvoiceService.mark_paid(invoice=invoice, subscription=subscription, actor=request.user)
        return Response(EmployerSubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=EmployerSubscriptionChangePlanSerializer, responses=EmployerSubscriptionSerializer)
    @action(detail=True, methods=["patch"], url_path="subscription/change-plan")
    def subscription_change_plan(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_manage_billing(employer, request.user)
        serializer = EmployerSubscriptionChangePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.validated_data["plan"]
        billing_cycle = serializer.validated_data["billing_cycle"]
        transaction_obj = PaymentService.initiate_subscription_payment(
            payer_user=request.user,
            employer=employer,
            plan=plan,
            billing_cycle=billing_cycle,
        )
        invoice = EmployerInvoiceService.create_for_subscription_checkout(
            employer=employer,
            plan=plan,
            billing_cycle=billing_cycle,
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        transaction_obj = PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=request.user)
        subscription = EmployerSubscriptionService.change_plan(
            employer=employer,
            plan=plan,
            billing_cycle=billing_cycle,
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        EmployerInvoiceService.mark_paid(invoice=invoice, subscription=subscription, actor=request.user)
        return Response(EmployerSubscriptionSerializer(subscription).data)

    @extend_schema(responses={201: EmployerSubscriptionSerializer})
    @action(detail=True, methods=["post"], url_path="subscription/renew")
    def subscription_renew(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_manage_billing(employer, request.user)
        current = EmployerSubscriptionService.current_for_employer(employer)
        if not current:
            raise ValidationError("No subscription is available to renew.")
        transaction_obj = PaymentService.initiate_subscription_payment(
            payer_user=request.user,
            employer=employer,
            plan=current.plan,
            billing_cycle=current.billing_cycle,
        )
        invoice = EmployerInvoiceService.create_for_subscription_checkout(
            employer=employer,
            plan=current.plan,
            billing_cycle=current.billing_cycle,
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        transaction_obj = PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=request.user)
        subscription = EmployerSubscriptionService.renew(
            employer=employer,
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        EmployerInvoiceService.mark_paid(invoice=invoice, subscription=subscription, actor=request.user)
        return Response(EmployerSubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=EmployerSubscriptionCancelSerializer, responses=EmployerSubscriptionSerializer)
    @action(detail=True, methods=["post"], url_path="subscription/cancel")
    def subscription_cancel(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_manage_billing(employer, request.user)
        serializer = EmployerSubscriptionCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = EmployerSubscriptionService.cancel(
            employer=employer,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(EmployerSubscriptionSerializer(subscription).data)

    @extend_schema(responses=EmployerSubscriptionSerializer)
    @action(detail=True, methods=["get"], url_path="subscription")
    def subscription(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_manage_billing(employer, request.user)
        subscription = EmployerSubscriptionService.current_for_employer(employer)
        if not subscription:
            return Response(None)
        return Response(EmployerSubscriptionSerializer(subscription).data)

    @extend_schema(responses=EmployerEntitlementSerializer)
    @action(detail=True, methods=["get"], url_path="subscription/entitlements")
    def subscription_entitlements(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_manage_billing(employer, request.user)
        return Response(EmployerSubscriptionService.entitlements_for_employer(employer))

    @extend_schema(responses=PaymentTransactionSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="payments")
    def payments(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_manage_billing(employer, request.user)
        return Response(PaymentTransactionSerializer(self._employer_billing_transactions(employer), many=True).data)

    @action(detail=True, methods=["get"], url_path="invoices")
    def invoices(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_manage_billing(employer, request.user)
        invoices = employer.invoices.select_related("subscription__plan", "payment_transaction").order_by("-issued_at")
        if invoices.exists():
            return Response(EmployerInvoiceSerializer(invoices, many=True).data)

        rows = []
        for transaction_obj in self._employer_billing_transactions(employer):
            rows.append({
                "id": str(transaction_obj.id),
                "invoice_number": f"INV-{transaction_obj.internal_reference}",
                "date": transaction_obj.created_at.date().isoformat(),
                "amount": str(transaction_obj.amount),
                "currency": transaction_obj.currency,
                "status": transaction_obj.status,
                "payment_reference": transaction_obj.provider_reference or transaction_obj.internal_reference,
                "receipt_url": None,
            })
        return Response(rows)

    @extend_schema(responses=EmployerUserSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="users")
    def employer_users(self, request, pk=None):
        employer = self.get_object()
        queryset = self._employer_staff_queryset(employer, request)
        return Response(EmployerUserSerializer(queryset, many=True).data)

    @extend_schema(request=EmployerInviteCreateSerializer, responses={201: EmployerInviteSerializer})
    @action(detail=True, methods=["get", "post"], url_path="invites")
    def employer_invites(self, request, pk=None):
        employer = self.get_object()
        if request.method == "GET":
            queryset = UserInvite.objects.select_related("organization", "unit", "invited_by", "accepted_by").filter(
                organization=employer.organization,
                role=UserRole.EMPLOYER,
            ).order_by("-created_at")
            if is_branch_manager(request.user) and request.user.unit_id:
                queryset = queryset.filter(unit=request.user.unit)
            status_filter = request.query_params.get("status")
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            return Response(EmployerInviteSerializer(queryset, many=True).data)

        self._ensure_can_manage_employer_staff(employer, request.user)
        serializer = EmployerInviteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data.get("unit")
        if unit and unit.organization_id != employer.organization_id:
            raise ValidationError("Invite unit must belong to this employer organization.")
        invite = InviteService.create_invite(
            actor=request.user,
            organization=employer.organization,
            email=serializer.validated_data["email"],
            role=UserRole.EMPLOYER,
            unit=unit,
            phone=serializer.validated_data.get("phone", ""),
            message=serializer.validated_data.get("message", ""),
            expires_at=serializer.validated_data.get("expires_at"),
        )
        invite.employer_staff_role = serializer.validated_data["employer_staff_role"]
        invite.save(update_fields=["employer_staff_role", "updated_at"])
        log_action(
            action=AuditAction.CREATE,
            actor=request.user,
            target=invite,
            metadata={"event": "employer_staff_invite", "employer_id": str(employer.id), "employer_staff_role": serializer.validated_data["employer_staff_role"]},
        )
        return Response(EmployerInviteSerializer(invite).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=EmployerUserUpdateSerializer, responses=EmployerUserSerializer)
    @action(detail=True, methods=["patch"], url_path="users/(?P<user_id>[^/.]+)")
    def employer_user_detail(self, request, pk=None, user_id=None):
        employer = self.get_object()
        self._ensure_can_manage_employer_staff(employer, request.user)
        target_user = User.objects.filter(id=user_id, organization=employer.organization, role=UserRole.EMPLOYER).first()
        if not target_user:
            raise ValidationError("Employer user not found.")
        if target_user.id == request.user.id and request.data.get("status") and request.data.get("status") != target_user.status:
            raise ValidationError("You cannot change your own status.")

        serializer = EmployerUserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data.get("unit")
        staff_role = serializer.validated_data.get("employer_staff_role")
        update_fields = ["updated_at"]
        if unit and unit.organization_id != employer.organization_id:
            raise ValidationError("Unit must belong to this employer organization.")
        if staff_role:
            target_user.employer_staff_role = staff_role
            if staff_role == EmployerStaffRole.BRANCH_MANAGER:
                target_user.unit = unit
                target_user.unit_restricted = True
            else:
                target_user.unit = None
                target_user.unit_restricted = False
            update_fields.extend(["employer_staff_role", "unit", "unit_restricted"])
        elif "unit" in serializer.validated_data:
            target_user.unit = unit
            target_user.unit_restricted = bool(unit)
            update_fields.extend(["unit", "unit_restricted"])
        if "status" in serializer.validated_data:
            target_user.status = serializer.validated_data["status"]
            update_fields.append("status")
        target_user.save(update_fields=sorted(set(update_fields)))
        log_action(action=AuditAction.UPDATE, actor=request.user, target=target_user, metadata={"event": "employer_user_updated", "employer_id": str(employer.id)})
        return Response(EmployerUserSerializer(target_user).data)

    @extend_schema(responses=EmployerInviteSerializer)
    @action(detail=True, methods=["delete"], url_path="invites/(?P<invite_id>[^/.]+)")
    def employer_invite_detail(self, request, pk=None, invite_id=None):
        employer = self.get_object()
        self._ensure_can_manage_employer_staff(employer, request.user)
        invite = UserInvite.objects.filter(id=invite_id, organization=employer.organization, role=UserRole.EMPLOYER).first()
        if not invite:
            raise ValidationError("Invite not found.")
        invite = InviteService.revoke(invite=invite, actor=request.user)
        return Response(EmployerInviteSerializer(invite).data)

    @action(detail=True, methods=["post"], url_path="food-handlers/(?P<fh_id>[^/.]+)/send-reminder")
    def send_reminder(self, request, pk=None, fh_id=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        fh = FoodHandlerProfile.objects.filter(id=fh_id, employer=employer).first()
        if not fh:
            raise ValidationError("Food handler not found under this employer.")
        reminder_type = request.data.get("type", "certificate")
        log_action(action=AuditAction.UPDATE, actor=request.user, target=fh, metadata={"event": "reminder_sent", "type": reminder_type})
        return Response({"detail": f"{reminder_type.replace('_', ' ').title()} reminder sent to {fh.full_name}."})

    @action(detail=True, methods=["get", "post"], url_path="illness-reports")
    def handle_illness_reports(self, request, pk=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)

        if request.method == "POST":
            user = request.user
            fh_id = request.data.get("food_handler")
            fh = FoodHandlerProfile.objects.filter(id=fh_id, employer=employer).first()
            if not fh:
                raise ValidationError("Food handler not found under this employer.")
            report = IllnessService.report(
                food_handler=fh,
                reported_by=user,
                symptoms=request.data.get("symptoms", {}),
                suspected_condition=request.data.get("suspected_condition", "other"),
                symptom_start_date=request.data.get("symptom_start_date"),
                notes=request.data.get("notes", ""),
            )
            return Response({
                "id": str(report.id),
                "food_handler_name": fh.full_name,
                "branch_name": fh.business_branch.name if fh.business_branch else None,
                "suspected_condition": report.suspected_condition,
                "symptoms": report.symptoms,
                "exclusion_start_date": report.exclusion_start_date.isoformat() if report.exclusion_start_date else None,
                "earliest_return_date": report.earliest_return_date.isoformat() if report.earliest_return_date else None,
                "clearance_status": report.clearance_status,
                "status": "submitted",
                "created_at": report.created_at.isoformat(),
            }, status=201)

        reports = IllnessReport.objects.select_related("food_handler", "food_handler__business_branch").filter(
            employer=employer
        ).order_by("-created_at")
        branch = request.query_params.get("branch")
        if branch:
            reports = reports.filter(food_handler__business_branch_id=branch)
        return Response([{
            "id": str(r.id),
            "food_handler_id": str(r.food_handler_id),
            "food_handler_name": r.food_handler.full_name,
            "branch_name": r.food_handler.business_branch.name if r.food_handler.business_branch else None,
            "suspected_condition": r.suspected_condition,
            "symptoms": r.symptoms,
            "symptom_start_date": r.symptom_start_date.isoformat() if r.symptom_start_date else None,
            "exclusion_start_date": r.exclusion_start_date.isoformat() if r.exclusion_start_date else None,
            "earliest_return_date": r.earliest_return_date.isoformat() if r.earliest_return_date else None,
            "clearance_status": r.clearance_status,
            "notes": r.notes,
            "created_at": r.created_at.isoformat(),
        } for r in reports])

    @action(detail=True, methods=["get"], url_path="illness-reports/(?P<report_id>[^/.]+)")
    def get_illness_report(self, request, pk=None, report_id=None):
        employer = self.get_object()
        self._ensure_can_view_employer_health_data(employer, request.user)
        r = IllnessReport.objects.select_related("food_handler", "food_handler__business_branch", "reviewed_by_doctor").filter(
            id=report_id, employer=employer
        ).first()
        if not r:
            raise ValidationError("Illness report not found.")
        return Response({
            "id": str(r.id),
            "food_handler_id": str(r.food_handler_id),
            "food_handler_name": r.food_handler.full_name,
            "branch_name": r.food_handler.business_branch.name if r.food_handler.business_branch else None,
            "suspected_condition": r.suspected_condition,
            "symptoms": r.symptoms,
            "symptom_start_date": r.symptom_start_date.isoformat() if r.symptom_start_date else None,
            "symptom_end_date": r.symptom_end_date.isoformat() if r.symptom_end_date else None,
            "exclusion_start_date": r.exclusion_start_date.isoformat() if r.exclusion_start_date else None,
            "earliest_return_date": r.earliest_return_date.isoformat() if r.earliest_return_date else None,
            "clearance_required": r.clearance_required,
            "clearance_status": r.clearance_status,
            "reviewed_by_doctor_name": r.reviewed_by_doctor.get_full_name() if r.reviewed_by_doctor else None,
            "return_to_work_certificate_number": r.return_to_work_certificate_number,
            "notes": r.notes,
            "created_at": r.created_at.isoformat(),
        })

    def _employer_inspections_queryset(self, employer, request):
        queryset = Inspection.objects.select_related("inspector", "employer", "branch").prefetch_related(
            "employer_responses"
        ).filter(employer=employer).order_by("-inspection_date")
        user = request.user
        if is_branch_manager(user) and user.unit_id:
            queryset = queryset.filter(branch=user.unit)
        branch = request.query_params.get("branch")
        if branch:
            queryset = queryset.filter(branch_id=branch)
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        date_from = request.query_params.get("date_from")
        if date_from:
            queryset = queryset.filter(inspection_date__date__gte=date_from)
        date_to = request.query_params.get("date_to")
        if date_to:
            queryset = queryset.filter(inspection_date__date__lte=date_to)
        return queryset

    def _inspection_summary(self, inspection):
        return {
            "id": str(inspection.id),
            "inspection_date": inspection.inspection_date.isoformat(),
            "inspector_name": inspection.inspector.get_full_name() or inspection.inspector.email,
            "branch": str(inspection.branch_id) if inspection.branch_id else None,
            "branch_name": inspection.branch.name if inspection.branch else None,
            "compliance_score": str(inspection.compliance_score) if inspection.compliance_score is not None else None,
            "findings_summary": inspection.findings[:180],
            "findings": inspection.findings,
            "enforcement_action": inspection.enforcement_action,
            "status": inspection.status,
            "follow_up_date": None,
            "response_count": inspection.employer_responses.count(),
            "submitted_at": inspection.submitted_at.isoformat() if inspection.submitted_at else None,
            "created_at": inspection.created_at.isoformat(),
            "updated_at": inspection.updated_at.isoformat(),
        }

    @action(detail=True, methods=["get"], url_path="inspections")
    def employer_inspections(self, request, pk=None):
        employer = self.get_object()
        queryset = self._employer_inspections_queryset(employer, request)
        return Response([self._inspection_summary(inspection) for inspection in queryset[:200]])

    @action(detail=True, methods=["get"], url_path="inspections/(?P<inspection_id>[^/.]+)")
    def employer_inspection_detail(self, request, pk=None, inspection_id=None):
        employer = self.get_object()
        inspection = self._employer_inspections_queryset(employer, request).filter(id=inspection_id).first()
        if not inspection:
            raise ValidationError("Inspection not found for this employer.")
        return Response({
            **self._inspection_summary(inspection),
            "checklist_responses": inspection.checklist_responses,
            "evidence_files": inspection.evidence_files,
            "gps_latitude": str(inspection.gps_latitude) if inspection.gps_latitude is not None else None,
            "gps_longitude": str(inspection.gps_longitude) if inspection.gps_longitude is not None else None,
            "responses": InspectionResponseSerializer(inspection.employer_responses.all(), many=True).data,
        })

    @extend_schema(request=InspectionResponseCreateSerializer, responses={201: InspectionResponseSerializer})
    @action(detail=True, methods=["post"], url_path="inspections/(?P<inspection_id>[^/.]+)/responses")
    def employer_inspection_response(self, request, pk=None, inspection_id=None):
        employer = self.get_object()
        inspection = self._employer_inspections_queryset(employer, request).filter(id=inspection_id).first()
        if not inspection:
            raise ValidationError("Inspection not found for this employer.")
        serializer = InspectionResponseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = InspectionService.submit_employer_response(
            inspection=inspection,
            actor=request.user,
            response_type=serializer.validated_data["response_type"],
            content=serializer.validated_data.get("content", ""),
            evidence_file_url=serializer.validated_data.get("evidence_file_url", ""),
        )
        return Response(InspectionResponseSerializer(response).data, status=status.HTTP_201_CREATED)

    def _report_filters(self, request):
        allowed = [
            "branch",
            "state",
            "lga",
            "category",
            "certificate_status",
            "fitness_status",
            "vaccine_type",
            "date_from",
            "date_to",
        ]
        return {key: request.query_params.get(key) for key in allowed if request.query_params.get(key)}

    def _report_format(self, request):
        return request.query_params.get("format") or request.query_params.get("file_format") or "json"

    def _generate_employer_report(self, *, request, employer, report_type):
        if employer.subscription_status in {EmployerSubscriptionStatus.EXPIRED, EmployerSubscriptionStatus.CANCELLED}:
            raise PermissionDenied("Premium report exports require an active employer subscription.")
        self._ensure_can_view_employer_health_data(employer, request.user)
        report = EmployerReportService.generate(
            report_type=report_type,
            employer=employer,
            actor=request.user,
            file_format=self._report_format(request),
            filters=self._report_filters(request),
        )
        return Response(GeneratedReportSerializer(report).data)

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["get"], url_path="reports/compliance")
    def compliance_report(self, request, pk=None):
        employer = self.get_object()
        return self._generate_employer_report(request=request, employer=employer, report_type=ReportType.EMPLOYER_COMPLIANCE)

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["get"], url_path="reports/certificates")
    def certificate_report(self, request, pk=None):
        employer = self.get_object()
        return self._generate_employer_report(request=request, employer=employer, report_type=ReportType.EMPLOYER_CERTIFICATES)

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["get"], url_path="reports/vaccinations")
    def vaccination_report(self, request, pk=None):
        employer = self.get_object()
        return self._generate_employer_report(request=request, employer=employer, report_type=ReportType.EMPLOYER_VACCINATIONS)
