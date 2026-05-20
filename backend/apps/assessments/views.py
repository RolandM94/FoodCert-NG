from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.assessments.models import Appointment, HealthDeclaration, MedicalAssessment
from apps.assessments.serializers import (
    AppointmentSerializer,
    CreateMedicalAssessmentSerializer,
    FitnessDecisionSerializer,
    HealthDeclarationSerializer,
    HealthDeclarationSubmitSerializer,
    MedicalAssessmentSerializer,
    PhysicalExaminationSerializer,
    PhysicalExaminationSubmitSerializer,
)
from apps.assessments.services import AssessmentService, ensure_approved_facility
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.lab_tests.serializers import LabTestRequestSerializer, LabTestSerializer
from apps.lab_tests.services import LabTestService
from apps.vaccinations.serializers import VaccinationRecordSerializer, VaccinationRecordSubmitSerializer
from apps.vaccinations.services import VaccinationService


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related("food_handler", "food_handler__employer", "facility", "facility__organization").order_by("-appointment_date")
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status", "facility", "food_handler"]
    ordering_fields = ["appointment_date", "created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
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
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.queryset.filter(facility__state=user.state)
        if user.role == UserRole.FOOD_HANDLER:
            return self.queryset.filter(food_handler__user=user)
        if user.role == UserRole.EMPLOYER and hasattr(user, "employer"):
            return self.queryset.filter(employer=user.employer)
        if user.organization_id:
            return self.queryset.filter(facility__organization=user.organization)
        return self.queryset.none()

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
            actor=request.user,
        )
        return Response(MedicalAssessmentSerializer(assessment).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=HealthDeclarationSubmitSerializer, responses={201: HealthDeclarationSerializer})
    @action(detail=True, methods=["post"], url_path="declaration")
    def declaration(self, request, pk=None):
        assessment = self.get_object()
        serializer = HealthDeclarationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data.get("certified_true"):
            raise ValidationError("Food handler must certify that declaration answers are true.")
        declaration = AssessmentService.submit_declaration(
            assessment=assessment,
            data=serializer.validated_data,
            actor=request.user,
        )
        return Response(HealthDeclarationSerializer(declaration).data, status=status.HTTP_201_CREATED)

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
        )
        return Response(MedicalAssessmentSerializer(assessment).data)


class HealthDeclarationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HealthDeclaration.objects.select_related("assessment", "assessment__facility", "assessment__food_handler", "validated_by_doctor")
    serializer_class = HealthDeclarationSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
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
