from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.locations.models import LGA, State, Ward
from apps.locations.serializers import LGASerializer, StateSerializer, WardSerializer


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.order_by("name")
    serializer_class = StateSerializer
    permission_classes = [AllowAny]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]

    @extend_schema(responses=LGASerializer(many=True))
    @action(detail=True, methods=["get"], url_path="lgas")
    def lgas(self, request, pk=None):
        state = self.get_object()
        queryset = state.lgas.order_by("name")
        return Response(LGASerializer(queryset, many=True).data)


class LGAViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LGA.objects.select_related("state").order_by("state__name", "name")
    serializer_class = LGASerializer
    permission_classes = [AllowAny]
    filterset_fields = ["state"]
    search_fields = ["name", "state__name"]
    ordering_fields = ["name", "state__name"]


class WardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ward.objects.select_related("lga", "lga__state").order_by("lga__name", "name")
    serializer_class = WardSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["lga", "lga__state"]
    search_fields = ["name", "lga__name"]
    ordering_fields = ["name", "lga__name"]
