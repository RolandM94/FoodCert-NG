from django.utils import timezone
from rest_framework import serializers

from apps.payments.models import Receipt
from apps.subscriptions.models import EmployerInvoice, EmployerSubscription, EmployerSubscriptionPlan


class EmployerSubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerSubscriptionPlan
        fields = (
            "id",
            "name",
            "description",
            "max_food_handlers",
            "max_locations",
            "max_users",
            "trial_days",
            "price_monthly",
            "price_yearly",
            "currency",
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
    max_users = serializers.IntegerField(source="plan.max_users", read_only=True)
    entitlements = serializers.SerializerMethodField()
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
            "grace_period_ends_at",
            "renewal_reminder_sent_at",
            "auto_renew",
            "cancellation_reason",
            "last_payment_transaction",
            "payment_reference",
            "is_active",
            "handlers_used",
            "max_food_handlers",
            "max_locations",
            "max_users",
            "entitlements",
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

    def get_entitlements(self, obj):
        from apps.subscriptions.services import EmployerSubscriptionService

        return EmployerSubscriptionService.entitlements_for_employer(obj.employer)


class EmployerSubscribeSerializer(serializers.Serializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=EmployerSubscriptionPlan.objects.all())
    billing_cycle = serializers.ChoiceField(choices=["monthly", "yearly"])


class EmployerSubscriptionCheckoutSerializer(serializers.Serializer):
    plan_id = serializers.PrimaryKeyRelatedField(queryset=EmployerSubscriptionPlan.objects.all(), source="plan")
    billing_cycle = serializers.ChoiceField(choices=["monthly", "yearly"])


class EmployerSubscriptionChangePlanSerializer(EmployerSubscriptionCheckoutSerializer):
    pass


class EmployerSubscriptionCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class EmployerEntitlementSerializer(serializers.Serializer):
    regulatory_access = serializers.BooleanField()
    premium_features_active = serializers.BooleanField()
    subscription_status = serializers.CharField()
    plan_id = serializers.CharField(allow_null=True)
    plan_name = serializers.CharField(allow_null=True)
    limits = serializers.DictField()
    features = serializers.DictField()
    restricted_features = serializers.ListField(child=serializers.CharField())


class EmployerInvoiceSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    amount = serializers.DecimalField(source="amount_due", max_digits=12, decimal_places=2, read_only=True)
    payment_reference = serializers.CharField(source="payment_transaction.internal_reference", read_only=True)
    receipt_url = serializers.SerializerMethodField()
    plan_name = serializers.CharField(source="subscription.plan.name", read_only=True)

    class Meta:
        model = EmployerInvoice
        fields = (
            "id",
            "invoice_number",
            "employer",
            "subscription",
            "plan_name",
            "payment_transaction",
            "payment_reference",
            "description",
            "line_items",
            "amount_due",
            "amount_paid",
            "amount",
            "currency",
            "status",
            "date",
            "due_date",
            "issued_at",
            "paid_at",
            "receipt_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_receipt_url(self, obj):
        if not obj.payment_transaction_id:
            return None
        receipt = Receipt.objects.filter(payment_transaction=obj.payment_transaction).first()
        return receipt.receipt_url if receipt else None

    def get_date(self, obj):
        return obj.issued_at.date().isoformat()
