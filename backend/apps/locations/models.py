from django.db import models

from apps.common.models import BaseModel


class State(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=16, unique=True)
    is_fct = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["code"])]

    def __str__(self) -> str:
        return self.name


class LGA(BaseModel):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="lgas")
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["state__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["state", "name"], name="unique_lga_per_state")
        ]
        indexes = [models.Index(fields=["state"])]

    def __str__(self) -> str:
        return f"{self.name}, {self.state.name}"


class Ward(BaseModel):
    lga = models.ForeignKey(LGA, on_delete=models.PROTECT, related_name="wards")
    name = models.CharField(max_length=120)

    class Meta:
        ordering = ["lga__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["lga", "name"], name="unique_ward_per_lga")
        ]
        indexes = [models.Index(fields=["lga"])]

    def __str__(self) -> str:
        return f"{self.name}, {self.lga.name}"
