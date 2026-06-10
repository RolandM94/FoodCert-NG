from django.db import models
from django_filters import rest_framework as filters
from rest_framework import generics, response, views
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.certificates.models import Certificate
from apps.employers.models import Employer
from apps.food_handlers.models import FoodHandlerProfile
from apps.organizations.models import OrganizationUnit
from apps.directory.serializers import (
    BranchDirectorySerializer,
    DirectoryPagination,
    EmployerDirectorySerializer,
    EmployerDirectoryDetailSerializer,
    FoodHandlerDirectorySerializer,
    FoodHandlerDirectoryDetailSerializer,
)
from apps.directory.services import DirectoryScopeService


class FoodHandlerFilter(filters.FilterSet):
    state = filters.UUIDFilter(field_name="state_id")
    lga = filters.UUIDFilter(field_name="lga_id")
    employer = filters.UUIDFilter(field_name="employer_id")
    branch = filters.UUIDFilter(field_name="business_branch_id")
    category = filters.CharFilter(field_name="food_handler_category")
    operational_fitness_status = filters.CharFilter(field_name="current_status")
    illness_exclusion_status = filters.CharFilter(method="filter_illness_exclusion_status")
    return_to_work_status = filters.CharFilter(method="filter_return_to_work_status")
    q = filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(full_name__icontains=value) |
            models.Q(system_identifier__icontains=value)
        )

    def filter_illness_exclusion_status(self, queryset, name, value):
        if value == "none":
            return queryset.exclude(illness_reports__clearance_status__in=["pending", "under_review", "clearance_required"]).distinct()
        return queryset.filter(illness_reports__clearance_status=value).distinct()

    def filter_return_to_work_status(self, queryset, name, value):
        if value == "not_required":
            return queryset.exclude(illness_reports__clearance_status__in=["pending", "under_review", "clearance_required"]).distinct()
        return queryset.filter(illness_reports__clearance_status=value).distinct()

    class Meta:
        model = FoodHandlerProfile
        fields = []


class FoodHandlerDirectoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = FoodHandlerDirectorySerializer
    pagination_class = DirectoryPagination
    filterset_class = FoodHandlerFilter
    search_fields = ["full_name", "system_identifier"]

    def get_queryset(self):
        scope = DirectoryScopeService(self.request.user)
        qs = FoodHandlerProfile.objects.select_related(
            "employer", "business_branch", "state", "lga"
        )
        qs = qs.filter(**scope.state_filter())
        qs = qs.filter(**scope.branch_filter())
        if self.request.user.role in {UserRole.EMPLOYER}:
            employer_filter = scope.employer_filter()
            if employer_filter:
                qs = qs.filter(**employer_filter)
        return qs.order_by("-created_at")


class FoodHandlerDirectoryDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = FoodHandlerDirectoryDetailSerializer
    queryset = FoodHandlerProfile.objects.select_related(
        "employer", "business_branch", "state", "lga"
    )


class EmployerFilter(filters.FilterSet):
    state = filters.UUIDFilter(field_name="state_id")
    lga = filters.UUIDFilter(field_name="lga_id")
    category = filters.CharFilter(field_name="establishment_category")
    compliance = filters.CharFilter(field_name="compliance_status")
    subscription = filters.CharFilter(field_name="subscription_status")
    q = filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(business_name__icontains=value) |
            models.Q(business_registration_number__icontains=value)
        )

    class Meta:
        model = Employer
        fields = []


class EmployerDirectoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = EmployerDirectorySerializer
    pagination_class = DirectoryPagination
    filterset_class = EmployerFilter

    def get_queryset(self):
        scope = DirectoryScopeService(self.request.user)
        qs = Employer.objects.select_related("state", "lga", "organization")
        qs = qs.filter(**scope.state_filter())
        if self.request.user.role == UserRole.EMPLOYER:
            ef = scope.employer_filter()
            if ef:
                qs = qs.filter(**ef)
        return qs.order_by("business_name")


class EmployerDirectoryDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = EmployerDirectoryDetailSerializer
    queryset = Employer.objects.select_related("state", "lga", "organization")


class BranchFilter(filters.FilterSet):
    employer = filters.UUIDFilter(field_name="organization__employer__id")
    state = filters.UUIDFilter(field_name="state_id")
    lga = filters.UUIDFilter(field_name="lga_id")
    q = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = OrganizationUnit
        fields = []


class BranchDirectoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = BranchDirectorySerializer
    pagination_class = DirectoryPagination
    filterset_class = BranchFilter

    def get_queryset(self):
        scope = DirectoryScopeService(self.request.user)
        qs = OrganizationUnit.objects.select_related(
            "organization", "organization__employer", "parent", "manager", "state", "lga"
        ).filter(
            unit_type__in=["branch", "outlet", "site", "store", "regional_office"]
        )
        qs = qs.filter(**scope.state_filter())
        if self.request.user.role == UserRole.EMPLOYER:
            ef = scope.employer_filter()
            if ef and "employer_id" in ef:
                qs = qs.filter(organization__employer_id=ef["employer_id"])
        return qs.order_by("name")


class BranchDirectoryDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = BranchDirectorySerializer
    queryset = OrganizationUnit.objects.select_related(
        "organization", "organization__employer", "parent", "manager", "state", "lga"
    ).filter(unit_type__in=["branch", "outlet", "site", "store", "regional_office"])


from django.db import models


class GlobalSearchView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 2:
            return response.Response({"results": {}})

        scope = DirectoryScopeService(request.user)

        results = {}
        if request.user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            fh = FoodHandlerProfile.objects.select_related("employer").filter(**scope.state_filter())
            if query:
                fh = fh.filter(models.Q(full_name__icontains=query) | models.Q(system_identifier__icontains=query))
            results["food_handlers"] = list(fh[:5].values("id", "full_name", "system_identifier", "employer__business_name"))

            emp = Employer.objects.select_related("state").filter(**scope.state_filter())
            if query:
                emp = emp.filter(business_name__icontains=query)
            results["employers"] = list(emp[:5].values("id", "business_name", "state__name"))

            cert = Certificate.objects.filter(**{k.replace("state_id", "issuing_state_id"): v for k, v in scope.state_filter().items()})
            if query:
                cert = cert.filter(certificate_number__icontains=query)
            results["certificates"] = list(cert[:5].values("id", "certificate_number", "status"))

        elif self.request.user.role == UserRole.EMPLOYER:
            ef = scope.employer_filter()
            fh = FoodHandlerProfile.objects.select_related("employer")
            if ef:
                fh = fh.filter(**ef)
            if query:
                fh = fh.filter(full_name__icontains=query)
            results["food_handlers"] = list(fh[:5].values("id", "full_name", "system_identifier", "employer__business_name"))

        return response.Response({"results": results})
