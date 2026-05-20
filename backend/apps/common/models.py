import uuid

from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StatusModel(models.Model):
    status = models.CharField(max_length=64, db_index=True)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel):
    class Meta:
        abstract = True
