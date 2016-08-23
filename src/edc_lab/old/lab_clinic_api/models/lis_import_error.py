from django.db import models

from edc_base.model.models import BaseUuidModel


class LisImportError(BaseUuidModel):

    model_name = models.CharField(max_length=25)

    identifier = models.CharField(max_length=25)

    subject_identifier = models.CharField(max_length=25, null=True)

    error_message = models.CharField(max_length=250)

    objects = models.Manager()

    class Meta:
        app_label = 'lab_clinic_api'
