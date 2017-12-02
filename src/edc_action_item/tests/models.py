from django.db import models
from edc_base.model_mixins import BaseUuidModel


class SubjectIdentifierModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)
