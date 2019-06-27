from django.apps import apps as django_apps
from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords


class DataDictionary(BaseUuidModel):

    model = models.CharField(max_length=250)

    model_verbose_name = models.CharField(max_length=250, null=True)

    number = models.IntegerField()

    prompt = models.TextField()

    field_name = models.CharField(max_length=250)

    field_type = models.CharField(max_length=250, null=True)

    max_length = models.IntegerField(null=True)

    decimal_places = models.IntegerField(null=True)

    max_digits = models.IntegerField(null=True)

    nullable = models.BooleanField(null=True)

    default = models.CharField(max_length=250, null=True)

    help_text = models.CharField(max_length=250, null=True)

    active = models.BooleanField(default=False)

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.model_verbose_name = self.get_model_verbose_name()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number}. {self.prompt} ({self.model_verbose_name})"

    def get_model_verbose_name(self):
        verbose_name = self.model
        try:
            model_cls = self.model_cls
        except (LookupError, ValueError):
            pass
        else:
            verbose_name = model_cls._meta.verbose_name
        return verbose_name

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)

    class Meta:
        default_permissions = ("view",)
        ordering = ("model", "number", "prompt")
        verbose_name = "Data Dictionary Item"
        verbose_name_plural = "Data Dictionary Items"
