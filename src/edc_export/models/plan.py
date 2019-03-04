from django.apps import apps as django_apps
from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords

MODEL_TYPES = (
    ("consent", "Consent"),
    ("crf", "CRF"),
    ("locator", "Locator"),
    ("plain", "Plain"),
)


class PlanManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Plan(BaseUuidModel):

    name = models.CharField(max_length=25, unique=True)

    model = models.CharField(max_length=50)

    field_names = models.TextField(max_length=500, blank=True, null=True)

    header_labels = models.TextField(max_length=500, blank=True, null=True)

    lookups = models.TextField(max_length=500, blank=True, null=True)

    model_type = models.CharField(max_length=25, choices=MODEL_TYPES, default="plain")

    excluded_field_names = models.TextField(max_length=500, blank=True, null=True)

    header = models.BooleanField(verbose_name="Include header", default=True)

    encrypt = models.BooleanField(verbose_name="Mask encrypted values", default=True)

    objects = PlanManager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} {self.model}"

    def save(self, *args, **kwargs):
        model_cls = django_apps.get_model(self.model)
        if not self.field_names:
            self.field_names = [f.name for f in model_cls._meta.get_fields()]
            self.field_names = ",".join(self.field_names)
        if not self.header_labels:
            self.header_labels = [f.name for f in model_cls._meta.get_fields()]
            self.header_labels = ",".join(self.header_labels)
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.name,)
