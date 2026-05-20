from rest_framework import serializers

from apps.locations.models import LGA, State, Ward


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ("id", "name", "code", "is_fct", "created_at", "updated_at")
        read_only_fields = fields


class LGASerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = LGA
        fields = ("id", "state", "state_name", "name", "created_at", "updated_at")
        read_only_fields = fields


class WardSerializer(serializers.ModelSerializer):
    lga_name = serializers.CharField(source="lga.name", read_only=True)

    class Meta:
        model = Ward
        fields = ("id", "lga", "lga_name", "name", "created_at", "updated_at")
        read_only_fields = fields
