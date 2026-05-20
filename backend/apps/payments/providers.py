from dataclasses import dataclass

from django.conf import settings


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


class PaymentProvider:
    provider_name = "base"

    def initialize_payment(self, amount, email, reference, metadata):
        raise NotImplementedError

    def verify_payment(self, reference):
        raise NotImplementedError

    def refund_payment(self, reference, amount=None):
        raise NotImplementedError


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


def get_payment_provider() -> PaymentProvider:
    if settings.PAYMENT_PROVIDER == "mock":
        return MockPaymentProvider()
    return MockPaymentProvider()
