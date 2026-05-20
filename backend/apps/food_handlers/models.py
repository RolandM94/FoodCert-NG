from django.db import models

from apps.common.models import BaseModel


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


class FoodHandlerCategory(models.TextChoices):
    KITCHEN_STAFF = "kitchen_staff", "Kitchen staff"
    FOOD_PREPARER = "food_preparer", "Food preparers"
    SERVING_CATERING = "serving_catering", "Serving and catering staff"
    FOOD_PACKER = "food_packer", "Food packers"
    BAKERY_WORKER = "bakery_worker", "Bakery workers"
    FOOD_PROCESSING_OPERATOR = "food_processing_operator", "Food processing operators"
    BARTENDER = "bartender", "Bartenders"
    DISHWASHER = "dishwasher", "Dishwashers"
    FOOD_DELIVERY = "food_delivery", "Food delivery personnel"
    STREET_VENDOR = "street_vendor", "Food stall and street food vendors"
    FOOD_STORAGE_HANDLER = "food_storage_handler", "Food storage handlers"
    CONCESSION_WORKER = "concession_worker", "Concession stand workers"
    AIRLINE_CATERING = "airline_catering", "Airline catering vendors"
    TRAIN_CATERING = "train_catering", "Train catering vendors"
    VESSEL_CATERING = "vessel_catering", "Cruise ship/sea vessel catering vendors"
    LIVESTOCK_MEAT = "livestock_meat", "Livestock farmers, butchers, meat cutters"
    EMERGENCY_FOOD_WORKER = "emergency_food_worker", "Emergency situation food workers"


class FoodHandlerStatus(models.TextChoices):
    PROFILE_INCOMPLETE = "profile_incomplete", "Profile Incomplete"
    NIN_PENDING = "nin_pending", "NIN Pending"
    CERTIFICATION_PENDING = "certification_pending", "Certification Pending"
    FIT = "fit", "Fit to Handle Food"
    TEMPORARILY_EXCLUDED = "temporarily_excluded", "Temporarily Excluded from Food Handling"
    TEMPORARILY_NOT_FIT = "temporarily_not_fit", "Temporarily Not Fit"
    EXCLUDED = "excluded", "Excluded from Food Handling"


class FoodHandlerProfile(BaseModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="food_handler_profile")
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=16, choices=Gender.choices)
    nin = models.CharField(max_length=32)
    passport_photo = models.ImageField(upload_to="passport_photos/", blank=True)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    nationality = models.CharField(max_length=80, default="Nigerian")
    home_address = models.TextField()
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="food_handlers")
    lga = models.ForeignKey("locations.LGA", on_delete=models.PROTECT, null=True, blank=True, related_name="food_handlers")
    ward = models.CharField(max_length=120, blank=True)
    employer = models.ForeignKey(
        "employers.Employer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="food_handlers",
    )
    business_branch = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="food_handlers",
    )
    work_location = models.TextField(blank=True)
    food_handler_category = models.CharField(max_length=64, choices=FoodHandlerCategory.choices)
    emergency_contact = models.CharField(max_length=255, blank=True)
    system_identifier = models.CharField(max_length=64, unique=True, db_index=True)
    current_status = models.CharField(
        max_length=32,
        choices=FoodHandlerStatus.choices,
        default=FoodHandlerStatus.PROFILE_INCOMPLETE,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["state"]),
            models.Index(fields=["lga"]),
            models.Index(fields=["employer"]),
            models.Index(fields=["business_branch"]),
            models.Index(fields=["current_status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.full_name

    @property
    def masked_nin(self) -> str:
        if not self.nin:
            return ""
        return f"{'*' * max(len(self.nin) - 4, 0)}{self.nin[-4:]}"
