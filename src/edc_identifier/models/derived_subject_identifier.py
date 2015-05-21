from django.db import models

from edc_base.model.models import BaseModel


class DerivedSubjectIdentifier(BaseModel):
    """Stores subject identifiers derived from another participant.

    For example:
        infant edc_identifier from maternal edc_identifier"""

    subject_identifier = models.CharField(
        max_length=25,
        unique=True)

    base_identifier = models.CharField(
        max_length=25)

    padding = models.IntegerField(null=True)

    def __str__(self):
        return self.subject_identifier

    class Meta:
        app_label = 'edc_identifier'
