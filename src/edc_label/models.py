from django.db import models
from edc_model.models import BaseUuidModel


class ZplLabelTemplates(BaseUuidModel):
    name = models.CharField(max_length=50, unique=True)

    zpl_data = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Label template"
        verbose_name_plural = "Label templates"
