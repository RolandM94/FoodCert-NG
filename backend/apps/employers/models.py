from django.db import models

from apps.common.models import BaseModel


class EstablishmentCategory(models.TextChoices):
    RESTAURANT_CAFE = "restaurant_cafe", "Restaurants and cafes"
    BAKERY = "bakery", "Bakeries and pastry shops"
    ABATTOIR_BUTCHER = "abattoir_butcher", "Abattoirs, slaughter slabs, and butcher shops"
    GROCERY_SUPERMARKET = "grocery_supermarket", "Grocery stores and supermarkets"
    FOOD_TRUCK_STREET_VENDOR = "food_truck_street_vendor", "Food trucks and street vendors"
    CATERING = "catering", "Catering services"
    SCHOOL_CAFETERIA = "school_cafeteria", "School cafeterias"
    HOSPITAL_KITCHEN = "hospital_kitchen", "Hospital kitchens"
    BAR_PUB = "bar_pub", "Bars and pubs"
    FOOD_PROCESSING_PLANT = "food_processing_plant", "Food processing plants"
    HOTEL_RESORT = "hotel_resort", "Hotels and resorts"
    CORPORATE_DINING = "corporate_dining", "Corporate dining facilities"
    FOOD_MARKET_STALL = "food_market_stall", "Food markets and stalls"
    FARM_FEED_PROCESSING = "farm_feed_processing", "Farms and livestock feed processing plants"
    DAYCARE = "daycare", "Daycare centres"


class ComplianceStatus(models.TextChoices):
    COMPLIANT = "compliant", "Compliant"
    NON_COMPLIANT = "non_compliant", "Non Compliant"
    UNDER_REVIEW = "under_review", "Under Review"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"
    NEVER_SUBSCRIBED = "never_subscribed", "Never Subscribed"


class Employer(BaseModel):
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="employer",
        null=True,
        blank=True,
    )
    organization = models.OneToOneField(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="employer",
        null=True,
        blank=True,
    )
    business_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100, blank=True, db_index=True)
    business_type = models.CharField(max_length=100, blank=True)
    establishment_category = models.CharField(max_length=64, choices=EstablishmentCategory.choices)
    contact_person_name = models.CharField(max_length=255)
    contact_person_phone = models.CharField(max_length=32)
    contact_person_email = models.EmailField()
    address = models.TextField()
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="employers")
    lga = models.ForeignKey("locations.LGA", on_delete=models.PROTECT, null=True, blank=True, related_name="employers")
    ward = models.CharField(max_length=120, blank=True)
    number_of_food_handlers = models.PositiveIntegerField(default=0)
    compliance_status = models.CharField(
        max_length=32,
        choices=ComplianceStatus.choices,
        default=ComplianceStatus.UNDER_REVIEW,
        db_index=True,
    )
    subscription_status = models.CharField(
        max_length=32,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.NEVER_SUBSCRIBED,
        db_index=True,
    )
    notification_preferences = models.JSONField(default=dict, blank=True)
    business_settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["state"], name="employers_e_state_i_81fb7b_idx"),
            models.Index(fields=["lga"], name="employers_e_lga_id_c01015_idx"),
            models.Index(fields=["compliance_status"], name="employers_e_complia_37e2c7_idx"),
            models.Index(fields=["subscription_status"], name="employers_e_subscri_b2f565_idx"),
        ]

    def __str__(self) -> str:
        return self.business_name
