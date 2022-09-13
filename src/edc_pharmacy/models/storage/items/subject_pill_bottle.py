from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin

from .pill_bottle_model_mixin import PillBottleModelMixin


class SubjectPillBottle(NonUniqueSubjectIdentifierFieldMixin, PillBottleModelMixin):

    rando_sid = models.CharField(max_length=25)

    class Meta(PillBottleModelMixin.Meta):
        verbose_name = "Subject Pill Bottle"
        verbose_name_plural = "Subject Pill Bottles"
