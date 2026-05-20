from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.utils import timezone


@dataclass
class NINProviderResponse:
    provider_reference: str
    full_name: str
    date_of_birth: object
    gender: str
    photo_url: str = ""


class BaseNINProvider:
    provider_name = "base"

    def verify_nin(self, food_handler) -> NINProviderResponse:
        raise NotImplementedError

    def calculate_match(self, food_handler, response: NINProviderResponse):
        mismatch_fields = {}
        score = Decimal("100.00")

        comparisons = {
            "full_name": (
                food_handler.full_name.strip().lower(),
                response.full_name.strip().lower(),
            ),
            "date_of_birth": (food_handler.date_of_birth, response.date_of_birth),
            "gender": (food_handler.gender, response.gender),
        }
        for field, (submitted, verified) in comparisons.items():
            if submitted != verified:
                mismatch_fields[field] = {"submitted": str(submitted), "verified": str(verified)}
                score -= Decimal("25.00")

        return max(score, Decimal("0.00")), mismatch_fields


class MockNINProvider(BaseNINProvider):
    provider_name = "mock"

    def verify_nin(self, food_handler) -> NINProviderResponse:
        if str(food_handler.nin).endswith("0000"):
            return NINProviderResponse(
                provider_reference=f"mock-{uuid4()}",
                full_name=f"{food_handler.full_name} Mismatch",
                date_of_birth=food_handler.date_of_birth,
                gender=food_handler.gender,
            )
        return NINProviderResponse(
            provider_reference=f"mock-{uuid4()}",
            full_name=food_handler.full_name,
            date_of_birth=food_handler.date_of_birth,
            gender=food_handler.gender,
        )


def get_nin_provider() -> BaseNINProvider:
    provider = settings.NIN_PROVIDER
    if provider == "mock":
        return MockNINProvider()
    return MockNINProvider()


def verification_timestamp_for_status(status: str):
    return timezone.now() if status == "verified" else None
