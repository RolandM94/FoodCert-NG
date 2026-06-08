from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.assessments.models import AssessmentFormQuestion, AssessmentFormResponse, AssessmentFormScope, AssessmentFormSection, AssessmentFormTemplate, AssessmentRequirementSet, Appointment, HealthDeclaration, MedicalAssessment
from apps.assessments.permissions import can_manage_assessment_form_template, can_manage_assessment_requirement_set
from apps.assessments.serializers import (
    AssessmentFormQuestionSerializer,
    AssessmentFormRejectionSerializer,
    AssessmentFormResponseDraftSerializer,
    AssessmentFormResponseReopenSerializer,
    AssessmentFormResponseSerializer,
    AssessmentFormResponseSummarySerializer,
    AssessmentFormSectionSerializer,
    AssessmentFormTemplateSerializer,
    AssessmentRequirementResolveSerializer,
    AssessmentRequirementSetSerializer,
    AssessmentAssignDoctorSerializer,
    AssessmentAuditTimelineItemSerializer,
    AssessmentStatusSnapshotSerializer,
    AppointmentAssignDoctorSerializer,
    AppointmentRescheduleSerializer,
    AppointmentSerializer,
    AppointmentTransitionSerializer,
    CreateMedicalAssessmentSerializer,
    DeclarationClarificationSerializer,
    DeclarationReopenSerializer,
    FitnessDecisionDraftSerializer,
    FitnessDecisionSerializer,
    FacilityAssessmentDetailSerializer,
    FacilityAssessmentSerializer,
    HealthDeclarationSerializer,
    HealthDeclarationSubmitSerializer,
    MedicalAssessmentSerializer,
    PhysicalExaminationSerializer,
    PhysicalExaminationSubmitSerializer,
)
from apps.assessments.services import AssessmentFormAnalyticsService, AssessmentFormResponseService, AssessmentFormTemplateService, AssessmentRequirementResolutionService, AssessmentService, ensure_approved_facility, ensure_assigned_doctor_for_assessment
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.serializers import CertificateRequestSerializer, RequestCertificateSerializer
from apps.certificates.services import CertificateService
from apps.lab_tests.serializers import LabTestRequestSerializer, LabTestSerializer
from apps.lab_tests.services import LabTestService
from apps.reports.models import GeneratedReport
from apps.reports.serializers import GeneratedReportSerializer
from apps.vaccinations.serializers import VaccinationRecordSerializer, VaccinationRecordSubmitSerializer, VaccinationReviewSerializer
from apps.vaccinations.services import VaccinationService


def assessment_form_templates_for_user(user):
    queryset = AssessmentFormTemplate.objects.select_related("state", "facility", "facility__organization", "owner_organization", "created_by", "approved_by", "parent_template").prefetch_related("sections__questions")
    if user.role == UserRole.SUPER_ADMIN:
        return queryset
    if user.role == UserRole.FEDERAL_ADMIN:
        return queryset.filter(scope=AssessmentFormScope.NATIONAL)
    if user.role == UserRole.STATE_ADMIN and user.state_id:
        return queryset.filter(Q(scope=AssessmentFormScope.STATE, state_id=user.state_id) | Q(scope=AssessmentFormScope.FACILITY, facility__state_id=user.state_id))
    if user.role == UserRole.FACILITY_ADMIN and user.organization_id:
        return queryset.filter(scope=AssessmentFormScope.FACILITY, facility__organization_id=user.organization_id)
    return queryset.none()


def assessment_requirement_sets_for_user(user):
    queryset = AssessmentRequirementSet.objects.select_related("state", "facility", "facility__organization", "created_by").prefetch_related("required_forms")
    if user.role == UserRole.SUPER_ADMIN:
        return queryset
    if user.role == UserRole.FEDERAL_ADMIN:
        return queryset.filter(scope=AssessmentFormScope.NATIONAL)
    if user.role == UserRole.STATE_ADMIN and user.state_id:
        return queryset.filter(Q(scope=AssessmentFormScope.STATE, state_id=user.state_id) | Q(scope=AssessmentFormScope.FACILITY, facility__state_id=user.state_id))
    if user.role == UserRole.FACILITY_ADMIN and user.organization_id:
        return queryset.filter(scope=AssessmentFormScope.FACILITY, facility__organization_id=user.organization_id)
    return queryset.none()


def medical_assessments_for_user(user):
    queryset = MedicalAssessment.objects.select_related(
        "food_handler", "food_handler__user", "employer", "facility", "facility__organization",
        "doctor", "appointment", "payment_transaction",
    ).order_by("-created_at")
    if user.role == UserRole.SUPER_ADMIN:
        return queryset
    if user.role == UserRole.FEDERAL_ADMIN:
        return queryset.none()
    if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
        return queryset.filter(facility__state=user.state)
    if user.role == UserRole.FOOD_HANDLER:
        return queryset.filter(food_handler__user=user)
    if user.role == UserRole.EMPLOYER and hasattr(user, "employer"):
        return queryset.filter(employer=user.employer)
    if user.organization_id:
        return queryset.filter(facility__organization=user.organization)
    return queryset.none()


def assessment_form_responses_for_user(user):
    queryset = AssessmentFormResponse.objects.select_related(
        "assessment", "assessment__food_handler", "assessment__food_handler__user", "assessment__facility",
        "assessment__facility__organization", "template", "respondent", "validated_by", "previous_response",
    )
    if user.role == UserRole.SUPER_ADMIN:
        return queryset
    if user.role == UserRole.FOOD_HANDLER:
        return queryset.filter(assessment__food_handler__user=user)
    if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and user.state_id:
        return queryset.filter(assessment__facility__state_id=user.state_id)
    if user.role == UserRole.EMPLOYER and hasattr(user, "employer"):
        return queryset.filter(assessment__employer=user.employer)
    if user.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF} and user.organization_id:
        return queryset.filter(assessment__facility__organization_id=user.organization_id)
    return queryset.none()


def uses_operational_form_response_summary(user):
    return user.role in {UserRole.EMPLOYER, UserRole.INSPECTOR}


def audit_sensitive_form_response_access(*, request, response, event):
    if uses_operational_form_response_summary(request.user):
        return
    log_action(
        action=AuditAction.MEDICAL_RECORD_ACCESS,
        actor=request.user,
        target=response,
        request=request,
        metadata={
            "event": event,
            "assessment_id": str(response.assessment_id),
            "template_id": str(response.template_id),
            "response_id": str(response.id),
        },
    )


class AssessmentFormTemplateViewSet(viewsets.ModelViewSet):
    queryset = AssessmentFormTemplate.objects.all()
    serializer_class = AssessmentFormTemplateSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return assessment_form_templates_for_user(self.request.user)

    def perform_create(self, serializer):
        values = dict(serializer.validated_data)
        if values.get("facility"):
            values["state"] = values["facility"].state
            values["owner_organization"] = values["facility"].organization
        candidate = AssessmentFormTemplate(**values)
        candidate.full_clean()
        if not can_manage_assessment_form_template(self.request.user, candidate):
            raise PermissionDenied("You cannot create an assessment form template for this scope.")
        template = serializer.save(created_by=self.request.user, state=values.get("state"), owner_organization=values.get("owner_organization"))
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=template, metadata={"event": "assessment_form_created"})

    def perform_update(self, serializer):
        template = self.get_object()
        AssessmentFormTemplateService.ensure_can_edit(template=template, actor=self.request.user)
        candidate = AssessmentFormTemplate.objects.get(pk=template.pk)
        for field, value in serializer.validated_data.items():
            setattr(candidate, field, value)
        if candidate.facility_id:
            candidate.state = candidate.facility.state
            candidate.owner_organization = candidate.facility.organization
        candidate.full_clean()
        if not can_manage_assessment_form_template(self.request.user, candidate):
            raise PermissionDenied("You cannot move this assessment form template into that scope.")
        template = serializer.save(state=candidate.state, owner_organization=candidate.owner_organization)
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=template, metadata={"event": "assessment_form_updated"})

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        duplicate = AssessmentFormTemplateService.duplicate(template=self.get_object(), actor=request.user)
        return Response(self.get_serializer(duplicate).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="submit-for-approval")
    def submit_for_approval(self, request, pk=None):
        template = AssessmentFormTemplateService.submit_for_approval(template=self.get_object(), actor=request.user)
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        template = AssessmentFormTemplateService.approve(template=self.get_object(), actor=request.user)
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        serializer = AssessmentFormRejectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = AssessmentFormTemplateService.reject(template=self.get_object(), actor=request.user, reason=serializer.validated_data["reason"])
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"], url_path="request-changes")
    def request_changes(self, request, pk=None):
        serializer = AssessmentFormRejectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = AssessmentFormTemplateService.request_changes(template=self.get_object(), actor=request.user, reason=serializer.validated_data["reason"])
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        template = AssessmentFormTemplateService.publish(template=self.get_object(), actor=request.user)
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        template = AssessmentFormTemplateService.activate(template=self.get_object(), actor=request.user)
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"], url_path="retire")
    def retire(self, request, pk=None):
        template = AssessmentFormTemplateService.retire(template=self.get_object(), actor=request.user)
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        template = self.get_object()
        root = template.parent_template or template
        versions = assessment_form_templates_for_user(request.user).filter(Q(id=root.id) | Q(parent_template=root)).order_by("version")
        return Response(self.get_serializer(versions, many=True).data)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        return Response(self.get_serializer(self.get_object()).data)


class AssessmentFormSectionViewSet(viewsets.ModelViewSet):
    queryset = AssessmentFormSection.objects.select_related("template").prefetch_related("questions")
    serializer_class = AssessmentFormSectionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return self.queryset.filter(template__in=assessment_form_templates_for_user(self.request.user))

    def perform_create(self, serializer):
        template = serializer.validated_data["template"]
        AssessmentFormTemplateService.ensure_can_edit(template=template, actor=self.request.user)
        section = serializer.save()
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=section, metadata={"event": "assessment_form_section_created", "template_id": str(template.id)})

    def perform_update(self, serializer):
        section = self.get_object()
        AssessmentFormTemplateService.ensure_can_edit(template=section.template, actor=self.request.user)
        if serializer.validated_data.get("template", section.template) != section.template:
            raise ValidationError("Sections cannot be moved between assessment form templates.")
        section = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=section, metadata={"event": "assessment_form_section_updated"})

    def perform_destroy(self, instance):
        AssessmentFormTemplateService.ensure_can_edit(template=instance.template, actor=self.request.user)
        log_action(action=AuditAction.DELETE, actor=self.request.user, target=instance, metadata={"event": "assessment_form_section_deleted"})
        instance.delete()


class AssessmentFormQuestionViewSet(viewsets.ModelViewSet):
    queryset = AssessmentFormQuestion.objects.select_related("section", "section__template")
    serializer_class = AssessmentFormQuestionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return self.queryset.filter(section__template__in=assessment_form_templates_for_user(self.request.user))

    def perform_create(self, serializer):
        section = serializer.validated_data["section"]
        AssessmentFormTemplateService.ensure_can_edit(template=section.template, actor=self.request.user)
        question = serializer.save()
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=question, metadata={"event": "assessment_form_question_created", "template_id": str(section.template_id)})

    def perform_update(self, serializer):
        question = self.get_object()
        AssessmentFormTemplateService.ensure_can_edit(template=question.section.template, actor=self.request.user)
        if serializer.validated_data.get("section", question.section) != question.section:
            raise ValidationError("Questions cannot be moved between assessment form sections.")
        question = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=question, metadata={"event": "assessment_form_question_updated"})

    def perform_destroy(self, instance):
        AssessmentFormTemplateService.ensure_can_edit(template=instance.section.template, actor=self.request.user)
        log_action(action=AuditAction.DELETE, actor=self.request.user, target=instance, metadata={"event": "assessment_form_question_deleted"})
        instance.delete()


class AssessmentRequirementSetViewSet(viewsets.ModelViewSet):
    queryset = AssessmentRequirementSet.objects.all()
    serializer_class = AssessmentRequirementSetSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return assessment_requirement_sets_for_user(self.request.user)

    def perform_create(self, serializer):
        values = dict(serializer.validated_data)
        values.pop("required_forms", None)
        if values.get("facility"):
            values["state"] = values["facility"].state
        candidate = AssessmentRequirementSet(**values)
        candidate.full_clean()
        if not can_manage_assessment_requirement_set(self.request.user, candidate):
            raise PermissionDenied("You cannot create an assessment requirement set for this scope.")
        requirement_set = serializer.save(created_by=self.request.user, state=values.get("state"))
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=requirement_set, metadata={"event": "assessment_requirement_set_created"})

    def perform_update(self, serializer):
        requirement_set = self.get_object()
        AssessmentRequirementResolutionService.ensure_can_manage(requirement_set=requirement_set, actor=self.request.user)
        if requirement_set.status != "draft":
            raise ValidationError("Only draft requirement sets can be edited.")
        candidate = AssessmentRequirementSet.objects.get(pk=requirement_set.pk)
        for field, value in serializer.validated_data.items():
            if field != "required_forms":
                setattr(candidate, field, value)
        if candidate.facility_id:
            candidate.state = candidate.facility.state
        candidate.full_clean()
        if not can_manage_assessment_requirement_set(self.request.user, candidate):
            raise PermissionDenied("You cannot move this requirement set into that scope.")
        requirement_set = serializer.save(state=candidate.state)
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=requirement_set, metadata={"event": "assessment_requirement_set_updated"})

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        requirement_set = AssessmentRequirementResolutionService.publish(requirement_set=self.get_object(), actor=request.user)
        return Response(self.get_serializer(requirement_set).data)

    @action(detail=True, methods=["post"], url_path="retire")
    def retire(self, request, pk=None):
        requirement_set = AssessmentRequirementResolutionService.retire(requirement_set=self.get_object(), actor=request.user)
        return Response(self.get_serializer(requirement_set).data)


class AssessmentRequirementResolveView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request):
        serializer = AssessmentRequirementResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = serializer.validated_data["assessment"]
        if not medical_assessments_for_user(request.user).filter(id=assessment.id).exists():
            raise PermissionDenied("You cannot resolve requirements for this assessment.")
        return Response(
            AssessmentRequirementResolutionService.resolve(
                assessment=assessment,
                actor=request.user,
                assessment_type=serializer.validated_data.get("assessment_type"),
            )
        )


class AssessmentFormAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        return Response(AssessmentFormAnalyticsService.aggregate(actor=request.user))


class AssessmentFormResponseViewSet(viewsets.ModelViewSet):
    queryset = AssessmentFormResponse.objects.all()
    serializer_class = AssessmentFormResponseSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "patch", "post", "head", "options"]
    filterset_fields = ["assessment", "template", "status", "respondent_role", "is_required", "is_locked"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return assessment_form_responses_for_user(self.request.user)

    def get_serializer_class(self):
        if getattr(self, "swagger_fake_view", False):
            return self.serializer_class
        if uses_operational_form_response_summary(self.request.user):
            return AssessmentFormResponseSummarySerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        response = self.get_object()
        audit_sensitive_form_response_access(
            request=request,
            response=response,
            event="assessment_form_response_read",
        )
        serializer = self.get_serializer(response)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        raise ValidationError("Assessment form responses are assigned from resolved requirements.")

    @extend_schema(request=AssessmentFormResponseDraftSerializer, responses=AssessmentFormResponseSerializer)
    def partial_update(self, request, *args, **kwargs):
        response = self.get_object()
        serializer = AssessmentFormResponseDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = AssessmentFormResponseService.save_draft(
            response=response,
            response_data=serializer.validated_data["response_data"],
            actor=request.user,
        )
        return Response(self.get_serializer(response).data)

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        response = AssessmentFormResponseService.submit(response=self.get_object(), actor=request.user)
        return Response(self.get_serializer(response).data)

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        response = AssessmentFormResponseService.mark_under_review(response=self.get_object(), actor=request.user)
        return Response(self.get_serializer(response).data)

    @action(detail=True, methods=["post"], url_path="validate")
    def validate_response(self, request, pk=None):
        response = AssessmentFormResponseService.validate(response=self.get_object(), actor=request.user)
        return Response(self.get_serializer(response).data)

    @extend_schema(request=AssessmentFormResponseReopenSerializer, responses=AssessmentFormResponseSerializer)
    @action(detail=True, methods=["post"], url_path="reopen")
    def reopen(self, request, pk=None):
        serializer = AssessmentFormResponseReopenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = AssessmentFormResponseService.reopen(
            response=self.get_object(),
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(self.get_serializer(response).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        response = self.get_object()
        audit_sensitive_form_response_access(
            request=request,
            response=response,
            event="assessment_form_response_versions_read",
        )
        versions = assessment_form_responses_for_user(request.user).filter(
            assessment=response.assessment,
            template=response.template,
        ).order_by("version")
        return Response(self.get_serializer(versions, many=True).data)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related(
        "food_handler",
        "food_handler__user",
        "food_handler__employer",
        "facility",
        "facility__organization",
        "doctor",
    ).prefetch_related("assessments__payment_transaction").order_by("-appointment_date")
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status", "facility", "food_handler"]
    ordering_fields = ["appointment_date", "created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        if user.role == UserRole.FEDERAL_ADMIN:
            return self.queryset.none()
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.queryset.filter(facility__state=user.state)
        if user.role == UserRole.FOOD_HANDLER:
            return self.queryset.filter(food_handler__user=user)
        if user.role == UserRole.EMPLOYER and hasattr(user, "employer"):
            return self.queryset.filter(food_handler__employer=user.employer)
        if user.organization_id:
            return self.queryset.filter(facility__organization=user.organization)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        food_handler = serializer.validated_data["food_handler"]
        facility = serializer.validated_data["facility"]
        ensure_approved_facility(facility)
        if user.role == UserRole.FOOD_HANDLER and food_handler.user_id != user.id:
            raise PermissionDenied("You can only book your own appointment.")
        user_employer = getattr(user, "employer", None)
        if user.role == UserRole.EMPLOYER and (not user_employer or getattr(food_handler, "employer_id", None) != user_employer.id):
            raise PermissionDenied("Employers can only book appointments for their own food handlers.")
        appointment = serializer.save()
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=user, target=appointment, metadata={"event": "appointment_created"})

    def perform_update(self, serializer):
        appointment = serializer.save()
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=self.request.user, target=appointment, metadata={"event": "appointment_updated"})

    @extend_schema(request=AppointmentTransitionSerializer, responses=AppointmentSerializer)
    @action(detail=True, methods=["patch"], url_path="confirm")
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.confirm_appointment(
            appointment=appointment,
            actor=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @extend_schema(request=AppointmentRescheduleSerializer, responses=AppointmentSerializer)
    @action(detail=True, methods=["patch"], url_path="reschedule")
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.reschedule_appointment(
            appointment=appointment,
            actor=request.user,
            appointment_date=serializer.validated_data["appointment_date"],
            reason=serializer.validated_data.get("reason", ""),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @extend_schema(request=AppointmentTransitionSerializer, responses=AppointmentSerializer)
    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.cancel_appointment(
            appointment=appointment,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @extend_schema(request=AppointmentTransitionSerializer, responses=AppointmentSerializer)
    @action(detail=True, methods=["patch"], url_path="no-show")
    def no_show(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.mark_appointment_no_show(
            appointment=appointment,
            actor=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @extend_schema(request=AppointmentAssignDoctorSerializer, responses=AppointmentSerializer)
    @action(detail=True, methods=["patch"], url_path="assign-doctor")
    def assign_doctor(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentAssignDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.assign_appointment_doctor(
            appointment=appointment,
            doctor=serializer.validated_data["doctor"],
            actor=request.user,
        )
        return Response(AppointmentSerializer(appointment).data)


class MedicalAssessmentViewSet(viewsets.ModelViewSet):
    queryset = MedicalAssessment.objects.select_related(
        "food_handler",
        "food_handler__user",
        "employer",
        "facility",
        "facility__organization",
        "doctor",
        "appointment",
        "payment_transaction",
    ).order_by("-created_at")
    serializer_class = MedicalAssessmentSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status", "facility", "food_handler", "final_decision"]
    ordering_fields = ["created_at", "assessment_date", "signed_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return medical_assessments_for_user(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        assessment = self.get_object()
        if request.user.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF}:
            log_action(
                action=AuditAction.MEDICAL_RECORD_ACCESS,
                actor=request.user,
                target=assessment,
                request=request,
                metadata={"event": "assessment_detail_read", "source": "assessment_api"},
            )
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(request=CreateMedicalAssessmentSerializer, responses={201: MedicalAssessmentSerializer})
    def create(self, request):
        serializer = CreateMedicalAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        food_handler = serializer.validated_data["food_handler"]
        if request.user.role == UserRole.FOOD_HANDLER and food_handler.user_id != request.user.id:
            raise PermissionDenied("You can only create your own assessment.")
        assessment = AssessmentService.create_assessment(
            food_handler=food_handler,
            facility=serializer.validated_data["facility"],
            payment_transaction=serializer.validated_data.get("payment_transaction"),
            appointment=serializer.validated_data.get("appointment"),
            assessment_type=serializer.validated_data["assessment_type"],
            actor=request.user,
        )
        return Response(MedicalAssessmentSerializer(assessment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="requirements")
    def requirements(self, request, pk=None):
        return Response(AssessmentRequirementResolutionService.resolve(assessment=self.get_object(), actor=request.user))

    @action(detail=True, methods=["get"], url_path="forms")
    def forms(self, request, pk=None):
        assessment = self.get_object()
        responses = assessment_form_responses_for_user(request.user).filter(assessment=assessment).exclude(status="superseded")
        return Response(AssessmentFormResponseSerializer(responses, many=True).data)

    @action(detail=True, methods=["post"], url_path="forms/assign")
    def assign_forms(self, request, pk=None):
        assessment = self.get_object()
        AssessmentRequirementResolutionService.assign_forms(assessment=assessment, actor=request.user)
        responses = assessment_form_responses_for_user(request.user).filter(assessment=assessment).exclude(status="superseded")
        return Response(AssessmentFormResponseSerializer(responses, many=True).data)

    @action(detail=True, methods=["get"], url_path=r"forms/(?P<template_id>[^/.]+)")
    def form_detail(self, request, pk=None, template_id=None):
        assessment = self.get_object()
        response = get_object_or_404(
            assessment_form_responses_for_user(request.user).exclude(status="superseded"),
            assessment=assessment,
            template_id=template_id,
        )
        return Response(AssessmentFormResponseSerializer(response).data)

    @extend_schema(responses=AssessmentStatusSnapshotSerializer)
    @action(detail=True, methods=["get"], url_path="status")
    def status_snapshot(self, request, pk=None):
        assessment = self.get_object()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=assessment,
            request=request,
            metadata={"event": "assessment_status_checked", "assessment_id": str(assessment.id)},
        )
        return Response(AssessmentService.status_snapshot(assessment))

    @extend_schema(responses=AssessmentAuditTimelineItemSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="audit-timeline")
    def audit_timeline(self, request, pk=None):
        assessment = self.get_object()
        log_action(
            action=AuditAction.MEDICAL_RECORD_ACCESS,
            actor=request.user,
            target=assessment,
            request=request,
            metadata={"event": "assessment_audit_timeline_viewed", "assessment_id": str(assessment.id)},
        )
        return Response(AssessmentService.assessment_timeline(assessment=assessment, user=request.user))

    @extend_schema(request=AppointmentTransitionSerializer, responses=MedicalAssessmentSerializer)
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        assessment = self.get_object()
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.cancel_assessment(
            assessment=assessment,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(MedicalAssessmentSerializer(assessment, context={"request": request}).data)

    @extend_schema(request=AppointmentTransitionSerializer, responses=MedicalAssessmentSerializer)
    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        assessment = self.get_object()
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.close_assessment(
            assessment=assessment,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(MedicalAssessmentSerializer(assessment, context={"request": request}).data)

    @extend_schema(request=HealthDeclarationSubmitSerializer, responses=HealthDeclarationSerializer)
    @action(detail=True, methods=["get", "patch", "post"], url_path="declaration")
    def declaration(self, request, pk=None):
        assessment = self.get_object()
        if request.method == "GET":
            declaration = getattr(assessment, "health_declaration", None)
            if not declaration:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            return Response(HealthDeclarationSerializer(declaration).data)

        serializer = HealthDeclarationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.method == "PATCH":
            declaration = AssessmentService.save_declaration_draft(
                assessment=assessment,
                data=serializer.validated_data,
                actor=request.user,
            )
            return Response(HealthDeclarationSerializer(declaration).data)

        declaration = AssessmentService.submit_declaration(
            assessment=assessment,
            data=serializer.validated_data,
            actor=request.user,
        )
        return Response(HealthDeclarationSerializer(declaration).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=HealthDeclarationSubmitSerializer, responses={201: HealthDeclarationSerializer})
    @action(detail=True, methods=["post"], url_path="declaration/submit")
    def submit_declaration(self, request, pk=None):
        assessment = self.get_object()
        serializer = HealthDeclarationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        declaration = AssessmentService.submit_declaration(
            assessment=assessment,
            data=serializer.validated_data,
            actor=request.user,
        )
        return Response(HealthDeclarationSerializer(declaration).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=HealthDeclarationSerializer)
    @action(detail=True, methods=["post"], url_path="declaration/validate")
    def validate_assessment_declaration(self, request, pk=None):
        assessment = self.get_object()
        declaration = get_object_or_404(HealthDeclaration, assessment=assessment)
        declaration = AssessmentService.validate_declaration(declaration=declaration, doctor=request.user)
        return Response(HealthDeclarationSerializer(declaration).data)

    @extend_schema(request=DeclarationReopenSerializer, responses=HealthDeclarationSerializer)
    @action(detail=True, methods=["post"], url_path="declaration/reopen")
    def reopen_declaration(self, request, pk=None):
        assessment = self.get_object()
        declaration = get_object_or_404(HealthDeclaration, assessment=assessment)
        serializer = DeclarationReopenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        declaration = AssessmentService.reopen_declaration(
            declaration=declaration,
            doctor=request.user,
            reason=serializer.validated_data["reason"],
        )
        return Response(HealthDeclarationSerializer(declaration).data)

    @extend_schema(request=PhysicalExaminationSubmitSerializer, responses={201: PhysicalExaminationSerializer})
    @action(detail=True, methods=["post"], url_path="physical-examination")
    def physical_examination(self, request, pk=None):
        assessment = self.get_object()
        serializer = PhysicalExaminationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = AssessmentService.complete_physical_exam(
            assessment=assessment,
            doctor=request.user,
            data=serializer.validated_data,
        )
        return Response(PhysicalExaminationSerializer(exam).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=PhysicalExaminationSubmitSerializer, responses=PhysicalExaminationSerializer)
    @action(detail=True, methods=["get", "post", "patch"], url_path="physical-exam")
    def physical_exam(self, request, pk=None):
        assessment = self.get_object()
        if request.method == "GET":
            exam = getattr(assessment, "physical_examination", None)
            if not exam:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            if request.user.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF}:
                log_action(
                    action=AuditAction.MEDICAL_RECORD_ACCESS,
                    actor=request.user,
                    target=assessment,
                    request=request,
                    metadata={"event": "physical_exam_read"},
                )
            return Response(PhysicalExaminationSerializer(exam).data)
        serializer = PhysicalExaminationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = AssessmentService.save_physical_exam_draft(
            assessment=assessment,
            doctor=request.user,
            data=serializer.validated_data,
        )
        return Response(PhysicalExaminationSerializer(exam).data)

    @extend_schema(request=PhysicalExaminationSubmitSerializer, responses={201: PhysicalExaminationSerializer})
    @action(detail=True, methods=["post"], url_path="physical-exam/complete")
    def complete_physical_exam(self, request, pk=None):
        assessment = self.get_object()
        serializer = PhysicalExaminationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = AssessmentService.complete_physical_exam(
            assessment=assessment,
            doctor=request.user,
            data=serializer.validated_data,
        )
        return Response(PhysicalExaminationSerializer(exam).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=LabTestRequestSerializer, responses={201: LabTestSerializer(many=True)})
    @action(detail=True, methods=["post"], url_path="lab-tests")
    def lab_tests(self, request, pk=None):
        assessment = self.get_object()
        serializer = LabTestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tests = LabTestService.request_tests(
            assessment=assessment,
            requested_by=request.user,
            tests=serializer.validated_data["tests"],
            include_required=serializer.validated_data.get("include_required", True),
        )
        return Response(LabTestSerializer(tests, many=True).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=VaccinationRecordSubmitSerializer, responses={201: VaccinationRecordSerializer})
    @action(detail=True, methods=["post"], url_path="vaccinations")
    def vaccinations(self, request, pk=None):
        assessment = self.get_object()
        serializer = VaccinationRecordSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = VaccinationService.record(
            assessment=assessment,
            recorded_by=request.user,
            data=serializer.validated_data,
        )
        return Response(VaccinationRecordSerializer(record).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=FitnessDecisionSerializer, responses=MedicalAssessmentSerializer)
    @action(detail=True, methods=["patch"], url_path="fitness-decision")
    def fitness_decision(self, request, pk=None):
        assessment = self.get_object()
        serializer = FitnessDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.set_fitness_decision(
            assessment=assessment,
            doctor=request.user,
            final_decision=serializer.validated_data["final_decision"],
            doctor_notes=serializer.validated_data.get("doctor_notes", ""),
            return_to_work_date=serializer.validated_data.get("return_to_work_date"),
            digital_signature_confirmation=serializer.validated_data.get("digital_signature_confirmation", False),
        )
        return Response(MedicalAssessmentSerializer(assessment).data)

    @extend_schema(request=RequestCertificateSerializer, responses={201: CertificateRequestSerializer})
    @action(detail=True, methods=["post"], url_path="submit-to-state")
    def submit_to_state(self, request, pk=None):
        assessment = self.get_object()
        serializer = RequestCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_request = CertificateService.submit_to_state(
            assessment=assessment,
            actor=request.user,
            notes=serializer.validated_data.get("request_notes", ""),
        )
        return Response(CertificateRequestSerializer(certificate_request).data, status=status.HTTP_201_CREATED)

    def _assessment_report(self, request, assessment, kind):
        if kind in {"medical", "lab", "vaccination"}:
            log_action(
                action=AuditAction.MEDICAL_RECORD_ACCESS,
                actor=request.user,
                target=assessment,
                request=request,
                metadata={"event": "assessment_report_read", "report_kind": kind},
            )
        report = AssessmentService.ensure_assessment_report(assessment=assessment, user=request.user, kind=kind)
        return Response(GeneratedReportSerializer(report).data)

    @extend_schema(responses=dict)
    @action(detail=True, methods=["get"], url_path="reports")
    def reports(self, request, pk=None):
        assessment = self.get_object()
        AssessmentService.ensure_assessment_report_access(assessment=assessment, user=request.user)
        generated = GeneratedReport.objects.filter(filters__assessment_id=str(assessment.id)).order_by("-created_at")
        return Response(
            {
                "available": ["summary", "medical", "return_to_work", "lab", "vaccination"],
                "generated": GeneratedReportSerializer(generated, many=True).data,
            }
        )

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["get"], url_path="reports/summary")
    def report_summary(self, request, pk=None):
        return self._assessment_report(request, self.get_object(), "summary")

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["get"], url_path="reports/medical")
    def report_medical(self, request, pk=None):
        return self._assessment_report(request, self.get_object(), "medical")

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["get"], url_path="reports/return-to-work")
    def report_return_to_work(self, request, pk=None):
        return self._assessment_report(request, self.get_object(), "return_to_work")

    @extend_schema(request=FitnessDecisionDraftSerializer, responses=MedicalAssessmentSerializer)
    @action(detail=True, methods=["patch"], url_path="fitness-decision/draft")
    def fitness_decision_draft(self, request, pk=None):
        assessment = self.get_object()
        serializer = FitnessDecisionDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.save_fitness_decision_draft(
            assessment=assessment,
            doctor=request.user,
            final_decision=serializer.validated_data["final_decision"],
            doctor_notes=serializer.validated_data.get("doctor_notes", ""),
            return_to_work_date=serializer.validated_data.get("return_to_work_date"),
        )
        return Response(MedicalAssessmentSerializer(assessment, context={"request": request}).data)

    @extend_schema(request=AssessmentAssignDoctorSerializer, responses=FacilityAssessmentSerializer)
    @action(detail=True, methods=["patch"], url_path="assign-doctor")
    def assign_doctor(self, request, pk=None):
        assessment = self.get_object()
        serializer = AssessmentAssignDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.assign_assessment_doctor(
            assessment=assessment,
            doctor=serializer.validated_data["doctor"],
            actor=request.user,
        )
        return Response(FacilityAssessmentSerializer(assessment, context={"request": request}).data)


class HealthDeclarationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HealthDeclaration.objects.select_related("assessment", "assessment__facility", "assessment__food_handler", "validated_by_doctor")
    serializer_class = HealthDeclarationSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        if user.role == UserRole.FEDERAL_ADMIN:
            return self.queryset.none()
        if user.role == UserRole.FOOD_HANDLER:
            return self.queryset.filter(assessment__food_handler__user=user)
        if user.role == UserRole.EMPLOYER:
            return self.queryset.none()
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.queryset.filter(assessment__facility__state=user.state)
        if user.organization_id:
            return self.queryset.filter(assessment__facility__organization=user.organization)
        return self.queryset.none()

    @extend_schema(responses=HealthDeclarationSerializer)
    @action(detail=True, methods=["patch"], url_path="validate")
    def validate(self, request, pk=None):
        declaration = get_object_or_404(self.get_queryset(), pk=pk)
        declaration = AssessmentService.validate_declaration(declaration=declaration, doctor=request.user)
        return Response(HealthDeclarationSerializer(declaration).data)


class DoctorAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FacilityAssessmentSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    lookup_url_kwarg = "assessment_id"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return MedicalAssessment.objects.none()
        user = self.request.user
        if user.role != UserRole.DOCTOR:
            return MedicalAssessment.objects.none()
        return (
            MedicalAssessment.objects.select_related(
                "food_handler",
                "food_handler__business_branch",
                "employer",
                "facility",
                "doctor",
                "appointment",
                "payment_transaction",
            )
            .prefetch_related("lab_tests", "vaccinations")
            .filter(facility__organization=user.organization, doctor=user)
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FacilityAssessmentDetailSerializer
        return FacilityAssessmentSerializer

    def retrieve(self, request, *args, **kwargs):
        assessment = self.get_object()
        log_action(
            action=AuditAction.MEDICAL_RECORD_ACCESS,
            actor=request.user,
            target=assessment,
            request=request,
            metadata={"event": "doctor_assessment_detail_read"},
        )
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(responses=HealthDeclarationSerializer)
    @action(detail=True, methods=["patch"], url_path="declaration/validate")
    def validate_declaration(self, request, assessment_id=None):
        assessment = self.get_object()
        ensure_assigned_doctor_for_assessment(request.user, assessment)
        declaration = get_object_or_404(HealthDeclaration, assessment=assessment)
        declaration = AssessmentService.validate_declaration(declaration=declaration, doctor=request.user)
        return Response(HealthDeclarationSerializer(declaration).data)

    @extend_schema(request=DeclarationClarificationSerializer, responses=HealthDeclarationSerializer)
    @action(detail=True, methods=["patch"], url_path="declaration/request-changes")
    def request_declaration_changes(self, request, assessment_id=None):
        assessment = self.get_object()
        ensure_assigned_doctor_for_assessment(request.user, assessment)
        declaration = get_object_or_404(HealthDeclaration, assessment=assessment)
        serializer = DeclarationClarificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        declaration = AssessmentService.request_declaration_clarification(
            declaration=declaration,
            doctor=request.user,
            reason=serializer.validated_data["reason"],
        )
        return Response(HealthDeclarationSerializer(declaration).data)

    @extend_schema(request=PhysicalExaminationSubmitSerializer, responses={201: PhysicalExaminationSerializer})
    @action(detail=True, methods=["post"], url_path="physical-exam")
    def physical_exam(self, request, assessment_id=None):
        assessment = self.get_object()
        ensure_assigned_doctor_for_assessment(request.user, assessment)
        serializer = PhysicalExaminationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = AssessmentService.complete_physical_exam(
            assessment=assessment,
            doctor=request.user,
            data=serializer.validated_data,
        )
        return Response(PhysicalExaminationSerializer(exam).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=PhysicalExaminationSubmitSerializer, responses=PhysicalExaminationSerializer)
    @action(detail=True, methods=["patch"], url_path="physical-exam/draft")
    def physical_exam_draft(self, request, assessment_id=None):
        assessment = self.get_object()
        ensure_assigned_doctor_for_assessment(request.user, assessment)
        serializer = PhysicalExaminationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = AssessmentService.save_physical_exam_draft(
            assessment=assessment,
            doctor=request.user,
            data=serializer.validated_data,
        )
        return Response(PhysicalExaminationSerializer(exam).data)

    @extend_schema(request=VaccinationReviewSerializer, responses=VaccinationRecordSerializer)
    @action(detail=True, methods=["patch"], url_path="vaccination-review")
    def vaccination_review(self, request, assessment_id=None):
        assessment = self.get_object()
        ensure_assigned_doctor_for_assessment(request.user, assessment)
        serializer = VaccinationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = VaccinationService.review_assessment(
            assessment=assessment,
            doctor=request.user,
            data=dict(serializer.validated_data),
        )
        return Response(VaccinationRecordSerializer(record, context={"request": request}).data)

    @extend_schema(request=FitnessDecisionSerializer, responses=FacilityAssessmentDetailSerializer)
    @action(detail=True, methods=["patch"], url_path="fitness-decision")
    def fitness_decision(self, request, assessment_id=None):
        assessment = self.get_object()
        ensure_assigned_doctor_for_assessment(request.user, assessment)
        serializer = FitnessDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.set_fitness_decision(
            assessment=assessment,
            doctor=request.user,
            final_decision=serializer.validated_data["final_decision"],
            doctor_notes=serializer.validated_data.get("doctor_notes", ""),
            return_to_work_date=serializer.validated_data.get("return_to_work_date"),
            digital_signature_confirmation=serializer.validated_data.get("digital_signature_confirmation", False),
        )
        return Response(FacilityAssessmentDetailSerializer(assessment, context={"request": request}).data)

    @extend_schema(request=FitnessDecisionDraftSerializer, responses=FacilityAssessmentDetailSerializer)
    @action(detail=True, methods=["patch"], url_path="fitness-decision/draft")
    def fitness_decision_draft(self, request, assessment_id=None):
        assessment = self.get_object()
        ensure_assigned_doctor_for_assessment(request.user, assessment)
        serializer = FitnessDecisionDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.save_fitness_decision_draft(
            assessment=assessment,
            doctor=request.user,
            final_decision=serializer.validated_data["final_decision"],
            doctor_notes=serializer.validated_data.get("doctor_notes", ""),
            return_to_work_date=serializer.validated_data.get("return_to_work_date"),
        )
        return Response(FacilityAssessmentDetailSerializer(assessment, context={"request": request}).data)
