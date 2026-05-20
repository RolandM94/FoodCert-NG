from rest_framework import serializers

from apps.certificates.models import Certificate, CertificateStatus
from apps.common.security import validate_uploaded_file_security
from apps.food_handlers.models import FoodHandlerProfile, FoodHandlerStatus
from apps.organizations.models import OrganizationUnit
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus, VaccineType


class FoodHandlerProfileSerializer(serializers.ModelSerializer):
    masked_nin = serializers.CharField(read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    business_branch_name = serializers.CharField(source="business_branch.name", read_only=True)

    class Meta:
        model = FoodHandlerProfile
        fields = (
            "id",
            "user",
            "full_name",
            "date_of_birth",
            "gender",
            "nin",
            "masked_nin",
            "passport_photo",
            "phone",
            "email",
            "nationality",
            "home_address",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "ward",
            "employer",
            "employer_name",
            "business_branch",
            "business_branch_name",
            "work_location",
            "food_handler_category",
            "emergency_contact",
            "system_identifier",
            "current_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "masked_nin", "system_identifier", "current_status", "created_at", "updated_at")
        extra_kwargs = {"nin": {"write_only": True}}

    def validate(self, attrs):
        employer = attrs.get("employer") or getattr(self.instance, "employer", None)
        branch = attrs.get("business_branch") or getattr(self.instance, "business_branch", None)
        if branch and employer and branch.organization_id != employer.organization_id:
            raise serializers.ValidationError("Business branch must belong to the employer organization.")
        return attrs

    def validate_passport_photo(self, value):
        return validate_uploaded_file_security(value, allowed_types={"image/jpeg", "image/png"})


FITNESS_TO_EMPLOYER_MAP = {
    FoodHandlerStatus.FIT: "fit_to_handle_food",
    FoodHandlerStatus.CERTIFICATION_PENDING: "certification_pending",
    FoodHandlerStatus.PROFILE_INCOMPLETE: "certification_pending",
    FoodHandlerStatus.NIN_PENDING: "certification_pending",
    FoodHandlerStatus.TEMPORARILY_NOT_FIT: "temporarily_not_fit",
    FoodHandlerStatus.TEMPORARILY_EXCLUDED: "excluded_from_food_handling",
    FoodHandlerStatus.EXCLUDED: "excluded_from_food_handling",
}

EMPLOYER_FITNESS_LABELS = {
    "fit_to_handle_food": "Fit to Handle Food",
    "certification_pending": "Certification Pending",
    "certificate_expired": "Certificate Expired",
    "certificate_expiring_soon": "Certificate Expiring Soon",
    "temporarily_not_fit": "Temporarily Not Fit",
    "excluded_from_food_handling": "Excluded from Food Handling",
    "return_to_work_pending": "Return-to-Work Pending",
    "cleared_to_return": "Cleared to Return to Work",
    "vaccination_due": "Vaccination Due",
    "medical_review_required": "Medical Review Required",
    "invite_pending": "Invite Pending",
    "not_linked": "Not Linked",
}


def _compute_employer_fitness(profile):
    status = profile.current_status
    base = FITNESS_TO_EMPLOYER_MAP.get(status, "certification_pending")

    if base == "fit_to_handle_food":
        cert = profile.certificates.filter(status=CertificateStatus.ACTIVE).order_by("-expiry_date").first()
        if cert:
            from django.utils import timezone
            today = timezone.localdate()
            days_left = (cert.expiry_date - today).days
            if days_left < 0:
                return "certificate_expired"
            if days_left <= 30:
                return "certificate_expiring_soon"
        else:
            latest = profile.certificates.order_by("-expiry_date").first()
            if latest and latest.status == CertificateStatus.ACTIVE:
                return "fit_to_handle_food"
            return "certification_pending"

    if base == "temporarily_excluded" or base == "excluded_from_food_handling":
        from apps.illness.models import IllnessReport
        clearance_exists = IllnessReport.objects.filter(
            food_handler=profile, clearance_status__in=["cleared", "under_review"]
        ).exists()
        if clearance_exists:
            return "return_to_work_pending"

    return base


class EmployerFoodHandlerListSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    business_branch_name = serializers.CharField(source="business_branch.name", read_only=True)
    fitness_status = serializers.SerializerMethodField()
    fitness_label = serializers.SerializerMethodField()
    certificate_number = serializers.SerializerMethodField()
    certificate_expiry_date = serializers.SerializerMethodField()
    certificate_status = serializers.SerializerMethodField()
    typhoid_status = serializers.SerializerMethodField()
    typhoid_expiry_date = serializers.SerializerMethodField()
    hepatitis_a_status = serializers.SerializerMethodField()
    last_assessment_date = serializers.SerializerMethodField()
    return_to_work_status = serializers.SerializerMethodField()

    class Meta:
        model = FoodHandlerProfile
        fields = (
            "id",
            "full_name",
            "passport_photo",
            "phone",
            "email",
            "state_name",
            "employer",
            "employer_name",
            "business_branch",
            "business_branch_name",
            "work_location",
            "food_handler_category",
            "current_status",
            "fitness_status",
            "fitness_label",
            "certificate_number",
            "certificate_expiry_date",
            "certificate_status",
            "typhoid_status",
            "typhoid_expiry_date",
            "hepatitis_a_status",
            "last_assessment_date",
            "return_to_work_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_fitness_status(self, obj):
        return _compute_employer_fitness(obj)

    def get_fitness_label(self, obj):
        return EMPLOYER_FITNESS_LABELS.get(_compute_employer_fitness(obj), "Unknown")

    def get_certificate_number(self, obj):
        cert = obj.certificates.filter(status=CertificateStatus.ACTIVE).order_by("-expiry_date").first()
        return cert.certificate_number if cert else None

    def get_certificate_expiry_date(self, obj):
        cert = obj.certificates.filter(status=CertificateStatus.ACTIVE).order_by("-expiry_date").first()
        return cert.expiry_date.isoformat() if cert and cert.expiry_date else None

    def get_certificate_status(self, obj):
        cert = obj.certificates.filter(status=CertificateStatus.ACTIVE).order_by("-expiry_date").first()
        if not cert:
            latest = obj.certificates.order_by("-expiry_date").first()
            return latest.status if latest else "no_certificate"
        return cert.status

    def get_typhoid_status(self, obj):
        vax = obj.vaccinations.filter(vaccine_type=VaccineType.TYPHOID).order_by("-date_administered").first()
        return vax.status if vax else "not_recorded"

    def get_typhoid_expiry_date(self, obj):
        vax = obj.vaccinations.filter(vaccine_type=VaccineType.TYPHOID, status=VaccinationStatus.VALID).order_by("-expiry_date").first()
        return vax.expiry_date.isoformat() if vax and vax.expiry_date else None

    def get_hepatitis_a_status(self, obj):
        dose1 = obj.vaccinations.filter(vaccine_type=VaccineType.HEPATITIS_A, dose_number=1).exists()
        dose2 = obj.vaccinations.filter(vaccine_type=VaccineType.HEPATITIS_A, dose_number=2).exists()
        if dose2:
            return "complete"
        if dose1:
            return "dose_1_completed"
        return "not_recorded"

    def get_last_assessment_date(self, obj):
        from apps.assessments.models import MedicalAssessment
        assmt = MedicalAssessment.objects.filter(food_handler=obj).order_by("-created_at").first()
        return assmt.assessment_date.isoformat() if assmt and assmt.assessment_date else None

    def get_return_to_work_status(self, obj):
        from apps.illness.models import IllnessReport
        report = IllnessReport.objects.filter(food_handler=obj).order_by("-created_at").first()
        if not report:
            return None
        return {
            "clearance_status": report.clearance_status,
            "exclusion_start_date": report.exclusion_start_date.isoformat() if report.exclusion_start_date else None,
            "earliest_return_date": report.earliest_return_date.isoformat() if report.earliest_return_date else None,
        }


class FoodHandlerBranchAssignmentSerializer(serializers.Serializer):
    business_branch = serializers.PrimaryKeyRelatedField(
        queryset=OrganizationUnit.objects.all(),
        required=False,
        allow_null=True,
    )
