from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_constants.constants import NEW
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_search.model_mixins import SearchSlugManager

from ..choices import PRESCRIPTION_STATUS
from .search_slug_model_mixin import SearchSlugModelMixin


class Manager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier, report_datetime):
        return self.get(
            subject_identifier=subject_identifier,
            report_datetime=report_datetime)


class Prescription(NonUniqueSubjectIdentifierFieldMixin,
                   SearchSlugModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    status = models.CharField(
        max_length=25,
        default=NEW,
        choices=PRESCRIPTION_STATUS)

    rando_sid = models.CharField(max_length=25, null=True)

    rando_arm = models.CharField(max_length=25, null=True)

    weight_in_kgs = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True)

    clinician_initials = models.CharField(
        max_length=3,
        null=True)

    notes = models.TextField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Private notes for pharmacist only')

    objects = Manager()

    def __str__(self):
        items = ', '.join(
            [str(obj) for obj in self.prescriptionitem_set.all()])
        return f'{items}'

    def natural_key(self):
        return (self.subject_identifier, self.report_datetime)

    @property
    def prescription_date(self):
        return self.report_datetime.date()
