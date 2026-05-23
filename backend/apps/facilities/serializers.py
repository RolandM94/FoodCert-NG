from rest_framework import serializers

from apps.accounts.models import UserInvite, UserRole
from apps.common.security import validate_uploaded_file_security
from apps.facilities.models import FacilityAccreditationApplication, FacilityDocument, FacilityStaffProfile, FacilityStaffType, MedicalFacility


class MedicalFacilitySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)
    can_conduct_assessments = serializers.BooleanField(read_only=True)
    profile_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = MedicalFacility
        fields = (
            "id",
            "organization",
            "facility_name",
            "facility_type",
            "ownership_type",
            "license_number",
            "registration_number",
            "address",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "ward",
            "contact_person",
            "phone",
            "email",
            "operating_hours",
            "service_capacity",
            "accreditation_status",
            "accreditation_start_date",
            "accreditation_expiry_date",
            "approved_by",
            "approved_by_name",
            "standard_assessment_price",
            "is_active",
            "can_conduct_assessments",
            "profile_complete",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "organization",
            "accreditation_status",
            "accreditation_start_date",
            "accreditation_expiry_date",
            "approved_by",
            "approved_by_name",
            "is_active",
            "can_conduct_assessments",
            "profile_complete",
            "created_at",
            "updated_at",
        )


class FacilityAccreditationApplicationSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    facility_state = serializers.CharField(source="facility.state.name", read_only=True)
    checklist_complete = serializers.BooleanField(read_only=True)
    reviewer_name = serializers.CharField(source="reviewer.get_full_name", read_only=True)

    class Meta:
        model = FacilityAccreditationApplication
        fields = (
            "id",
            "facility",
            "facility_name",
            "facility_state",
            "application_status",
            "has_reporting_policy",
            "has_medical_records_computers",
            "has_computer_operators",
            "has_standard_forms",
            "has_laboratory_request_forms",
            "has_patient_files",
            "has_qr_certificate_capability",
            "has_internet_access",
            "has_trained_records_staff",
            "has_trained_clinical_staff",
            "has_trained_non_clinical_staff",
            "has_valid_facility_license",
            "has_laboratory_capacity",
            "has_valid_doctor_credentials",
            "has_valid_lab_staff_credentials",
            "has_infection_prevention_readiness",
            "has_confidentiality_policy",
            "supporting_document",
            "is_renewal",
            "renewal_of",
            "checklist_complete",
            "reviewer",
            "reviewer_name",
            "review_comment",
            "submitted_at",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "application_status",
            "checklist_complete",
            "reviewer",
            "reviewer_name",
            "review_comment",
            "is_renewal",
            "renewal_of",
            "submitted_at",
            "reviewed_at",
            "created_at",
            "updated_at",
        )

    def validate_supporting_document(self, value):
        return validate_uploaded_file_security(value)


class AccreditationReviewSerializer(serializers.Serializer):
    review_comment = serializers.CharField(required=False, allow_blank=True)


class FacilityDocumentSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    uploaded_by_name = serializers.CharField(source="uploaded_by.get_full_name", read_only=True)
    file_url = serializers.FileField(source="file", read_only=True)

    class Meta:
        model = FacilityDocument
        fields = (
            "id",
            "facility",
            "facility_name",
            "accreditation_application",
            "document_type",
            "file",
            "file_url",
            "status",
            "uploaded_by",
            "uploaded_by_name",
            "review_comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "facility_name",
            "file_url",
            "status",
            "uploaded_by",
            "uploaded_by_name",
            "review_comment",
            "created_at",
            "updated_at",
        )

    def validate_file(self, value):
        return validate_uploaded_file_security(value)

    def validate(self, attrs):
        application = attrs.get("accreditation_application")
        facility = attrs.get("facility")
        if application and facility and application.facility_id != facility.id:
            raise serializers.ValidationError("Document application must belong to the selected facility.")
        return attrs


class FacilityStaffProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    user_status = serializers.CharField(source="user.status", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    last_login = serializers.DateTimeField(source="user.last_login", read_only=True)

    class Meta:
        model = FacilityStaffProfile
        fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "user_role",
            "user_status",
            "facility",
            "department",
            "department_name",
            "staff_type",
            "professional_registration_number",
            "digital_signature_url",
            "is_active",
            "last_login",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "user_role",
            "user_status",
            "facility",
            "department_name",
            "last_login",
            "created_at",
            "updated_at",
        )

    def validate_department(self, department):
        facility = self.context.get("facility")
        if department and facility and department.organization_id != facility.organization_id:
            raise serializers.ValidationError("Department must belong to this facility.")
        return department


class FacilityStaffInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=[UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF])
    staff_type = serializers.ChoiceField(choices=FacilityStaffType.choices)
    department = serializers.UUIDField(required=False, allow_null=True)
    professional_registration_number = serializers.CharField(required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False)


class FacilityInviteSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    invited_by_email = serializers.EmailField(source="invited_by.email", read_only=True)

    class Meta:
        model = UserInvite
        fields = (
            "id",
            "organization",
            "organization_name",
            "unit",
            "unit_name",
            "invited_by",
            "invited_by_email",
            "email",
            "phone",
            "role",
            "facility_staff_type",
            "message",
            "status",
            "expires_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
