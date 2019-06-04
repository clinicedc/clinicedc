from django.apps import apps as django_apps
from django.db import models
from edc_model.models import BaseUuidModel
from edc_model.models.historical_records import HistoricalRecords


class DataDictionary(BaseUuidModel):

    model = models.CharField(max_length=250)

    field_name = models.CharField(max_length=250)

    number = models.IntegerField()

    prompt = models.TextField()

    active = models.BooleanField(default=False)

    field_type = models.CharField(max_length=250, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.number}. {self.prompt} ({self.model_verbose_name})"

    @property
    def model_verbose_name(self):
        verbose_name = self.model
        try:
            model_cls = django_apps.get_model(self.model)
        except (LookupError, ValueError):
            pass
        else:
            verbose_name = model_cls._meta.verbose_name
        return verbose_name

    class Meta:
        ordering = ("model", "number", "prompt")
        verbose_name = "Data Dictionary Item"
        verbose_name_plural = "Data Dictionary Items"
