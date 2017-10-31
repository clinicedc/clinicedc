from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins.base_uuid_model import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_constants.constants import NEW
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin

from ..choices import DISPENSE_STATUS
from .prescription_item import PrescriptionItem
from .prescription import Prescription


class DispenseError(Exception):
    pass


class DispensedItem(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    prescription = models.ForeignKey(Prescription, on_delete=PROTECT)

    prescription_item = models.ForeignKey(PrescriptionItem, on_delete=PROTECT)

    dispensed_datetime = models.DateTimeField(
        default=get_utcnow)

    dispensed = models.DecimalField(max_digits=6, decimal_places=1)

    status = models.CharField(
        verbose_name='Dispensed',
        max_length=25,
        default=NEW,
        choices=DISPENSE_STATUS)

    def __str__(self):
        return f'{str(self.prescription)}'

    def save(self, *args, **kwargs):
        self.prescription = self.prescription_item.prescription
        self.subject_identifier = self.prescription.subject_identifier
        if self.prescription_item.get_remaining(exclude_id=self.id) < self.dispensed:
            raise DispenseError('Attempt to dispense more than prescribed.')
        super().save(*args, **kwargs)

    @property
    def dispensed_date(self):
        return self.dispensed_datetime.date()
