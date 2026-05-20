from django.utils import timezone
from rest_framework import serializers

from apps.subscriptions.models import EmployerSubscription, EmployerSubscriptionPlan


class EmployerSubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerSubscriptionPlan
        fields = (
            "id",
            "name",
            "description",
            "max_food_handlers",
            "max_locations",
            "price_monthly",
            "price_yearly",
            "features",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EmployerSubscriptionSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    handlers_used = serializers.IntegerField(source="employer.food_handlers.count", read_only=True)
    max_food_handlers = serializers.IntegerField(source="plan.max_food_handlers", read_only=True)
    max_locations = serializers.IntegerField(source="plan.max_locations", read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    payment_reference = serializers.CharField(source="last_payment_transaction.internal_reference", read_only=True)

    class Meta:
        model = EmployerSubscription
        fields = (
            "id",
            "employer",
            "employer_name",
            "plan",
            "plan_name",
            "billing_cycle",
            "status",
            "starts_at",
            "expires_at",
            "cancelled_at",
            "last_payment_transaction",
            "payment_reference",
            "is_active",
            "handlers_used",
            "max_food_handlers",
            "max_locations",
            "days_until_expiry",
            "usage_percentage",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_days_until_expiry(self, obj) -> int:
        return max((obj.expires_at - timezone.now()).days, 0)

    def get_usage_percentage(self, obj) -> float:
        max_handlers = obj.plan.max_food_handlers
        if not max_handlers:
            return 0
        return round((obj.employer.food_handlers.count() / max_handlers) * 100, 2)


class EmployerSubscribeSerializer(serializers.Serializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=EmployerSubscriptionPlan.objects.all())
    billing_cycle = serializers.ChoiceField(choices=["monthly", "yearly"])


class EmployerSubscriptionCheckoutSerializer(serializers.Serializer):
    plan_id = serializers.PrimaryKeyRelatedField(queryset=EmployerSubscriptionPlan.objects.all(), source="plan")
    billing_cycle = serializers.ChoiceField(choices=["monthly", "yearly"])


class EmployerSubscriptionChangePlanSerializer(EmployerSubscriptionCheckoutSerializer):
    pass
