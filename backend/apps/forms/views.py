from rest_framework import viewsets, status, response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsActiveUser
from apps.forms.models import (
    AssignmentStatus,
    FormAssignment,
    FormResponse,
    FormTemplate,
    FormTemplateStatus,
    FormTemplateVersion,
    ResponseStatus,
)
from apps.forms.serializers import (
    FormAssignmentSerializer,
    FormResponseSerializer,
    FormTemplateSerializer,
    FormTemplateVersionSerializer,
)


class FormTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = FormTemplateSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = FormTemplate.objects.select_related("owner_organization", "created_by")
        purpose = self.request.query_params.get("purpose")
        status_param = self.request.query_params.get("status")
        if purpose:
            qs = qs.filter(purpose=purpose)
        if status_param:
            qs = qs.filter(status=status_param)
        if user.role not in {"super_admin", "federal_admin", "state_admin"}:
            qs = qs.filter(owner_organization_id=getattr(user, "organization_id", None))
        return qs.order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        template = self.get_object()
        if template.status != FormTemplateStatus.DRAFT:
            return response.Response({"error": "Only draft templates can be published."}, status=400)
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=template.current_version,
            schema_json={"sections": [], "questions": []},
            published_by=request.user,
            status=FormTemplateStatus.PUBLISHED,
        )
        template.status = FormTemplateStatus.PUBLISHED
        template.save(update_fields=["status", "updated_at"])
        version.published_at = version.created_at
        version.save(update_fields=["published_at"])
        return response.Response(FormTemplateSerializer(template).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        template = self.get_object()
        template.status = FormTemplateStatus.ARCHIVED
        template.save(update_fields=["status", "updated_at"])
        return response.Response(FormTemplateSerializer(template).data)

    @action(detail=True, methods=["post"])
    def new_version(self, request, pk=None):
        template = self.get_object()
        template.current_version += 1
        template.status = FormTemplateStatus.DRAFT
        template.save(update_fields=["current_version", "status", "updated_at"])
        return response.Response(FormTemplateSerializer(template).data)

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        template = self.get_object()
        versions = template.versions.order_by("-version_number")
        return response.Response(FormTemplateVersionSerializer(versions, many=True).data)

    @action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        template = self.get_object()
        latest = template.versions.order_by("-version_number").first()
        data = FormTemplateSerializer(template).data
        data["schema"] = latest.schema_json if latest else {}
        return response.Response(data)


class FormAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = FormAssignmentSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = FormAssignment.objects.select_related("template", "assigned_by")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        if user.role not in {"super_admin", "federal_admin", "state_admin"}:
            qs = qs.filter(assigned_to_id=str(user.organization_id))
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        assignment = self.get_object()
        assignment.status = AssignmentStatus.CANCELLED
        assignment.save(update_fields=["status", "updated_at"])
        return response.Response(FormAssignmentSerializer(assignment).data)


class FormResponseViewSet(viewsets.ModelViewSet):
    serializer_class = FormResponseSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = FormResponse.objects.select_related(
            "assignment", "template", "respondent_user", "reviewed_by"
        )
        status_param = self.request.query_params.get("status")
        assignment_id = self.request.query_params.get("assignment")
        if status_param:
            qs = qs.filter(status=status_param)
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        if user.role not in {"super_admin", "federal_admin", "state_admin"}:
            qs = qs.filter(respondent_user=user)
        return qs.order_by("-created_at")

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        r = self.get_object()
        r.status = ResponseStatus.SUBMITTED
        r.submitted_at = r.updated_at
        r.response_json = request.data.get("response_json", r.response_json)
        r.score = request.data.get("score", r.score)
        r.save()
        return response.Response(FormResponseSerializer(r).data)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        r = self.get_object()
        r.status = ResponseStatus.REVIEWED
        r.reviewed_by = request.user
        r.reviewed_at = r.updated_at
        r.review_notes = request.data.get("review_notes", "")
        r.save()
        return response.Response(FormResponseSerializer(r).data)

    @action(detail=True, methods=["post"])
    def return_response(self, request, pk=None):
        r = self.get_object()
        r.status = ResponseStatus.RETURNED
        r.returned_reason = request.data.get("reason", "")
        r.save()
        return response.Response(FormResponseSerializer(r).data)
