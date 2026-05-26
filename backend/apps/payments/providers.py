from dataclasses import dataclass
import hashlib
import hmac

from django.conf import settings

from apps.payments.models import PaymentProvider as PaymentProviderConfig


@dataclass
class PaymentInitialization:
    provider_reference: str
    authorization_url: str
    metadata: dict


@dataclass
class PaymentVerification:
    provider_reference: str
    status: str
    amount: str
    metadata: dict


@dataclass
class PaymentWebhookPayload:
    reference: str
    event_type: str
    provider_reference: str
    idempotency_key: str
    metadata: dict


class PaymentProvider:
    provider_name = "base"

    def initialize_payment(self, amount, email, reference, metadata):
        raise NotImplementedError

    def verify_payment(self, reference):
        raise NotImplementedError

    def refund_payment(self, reference, amount=None):
        raise NotImplementedError

    def verify_webhook_signature(self, *, body: bytes, signature: str, secret: str = "") -> bool:
        if not secret:
            return True
        expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)

    def parse_webhook_payload(self, payload: dict) -> PaymentWebhookPayload:
        reference = payload.get("reference") or payload.get("data", {}).get("reference") or ""
        event_type = payload.get("event") or payload.get("event_type") or ""
        provider_reference = payload.get("provider_reference") or payload.get("data", {}).get("reference") or reference
        idempotency_key = payload.get("idempotency_key") or payload.get("event_id") or f"{self.provider_name}:{event_type}:{provider_reference}"
        return PaymentWebhookPayload(
            reference=reference,
            event_type=event_type,
            provider_reference=provider_reference,
            idempotency_key=idempotency_key,
            metadata=payload,
        )


class MockPaymentProvider(PaymentProvider):
    provider_name = "mock"

    def initialize_payment(self, amount, email, reference, metadata):
        return PaymentInitialization(
            provider_reference=f"mock-{reference}",
            authorization_url=f"https://mock-payments.foodcert.local/pay/{reference}",
            metadata={"email": email, **metadata},
        )

    def verify_payment(self, reference):
        status = "failed" if str(reference).endswith("FAIL") else "success"
        return PaymentVerification(
            provider_reference=f"mock-{reference}",
            status=status,
            amount="0.00",
            metadata={"verified": True},
        )

    def refund_payment(self, reference, amount=None):
        return {"reference": reference, "amount": str(amount) if amount else None, "status": "refunded"}


def active_provider_config(provider_code=None):
    code = provider_code or getattr(settings, "PAYMENT_PROVIDER", "mock")
    return PaymentProviderConfig.objects.filter(code=code, is_active=True).first()


def get_payment_provider(provider_code=None) -> PaymentProvider:
    code = provider_code or getattr(settings, "PAYMENT_PROVIDER", "mock")
    if code == "mock":
        return MockPaymentProvider()
    return MockPaymentProvider()
