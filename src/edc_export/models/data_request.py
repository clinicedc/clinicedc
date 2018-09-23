from django.apps import apps as django_apps
from django.db import models
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel

from ..choices import EXPORT_FORMATS
from ..constants import CSV


class DataRequest(BaseUuidModel):

    name = models.CharField(max_length=25)

    description = models.TextField(null=True)

    decrypt = models.BooleanField(default=False)

    export_format = models.CharField(
        max_length=25,
        choices=EXPORT_FORMATS,
        default=CSV)

    models = models.TextField(
        help_text='List one table per line, no commas. Use "label lower" format.')

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    @property
    def models_as_list(self):
        """Returns `models` as a list.

        Validates each item to be a model name.
        """
        models_as_list = self.models.split('\n')
        models_as_list = [x.strip() for x in models_as_list if x.strip()]
        for model in models_as_list:
            django_apps.get_model(model)
        return models_as_list

    class Meta:
        ordering = ('name', )
