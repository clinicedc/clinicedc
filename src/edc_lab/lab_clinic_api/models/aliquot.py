from django.db import models
from django.core.exceptions import ValidationError

from lis.specimen.lab_aliquot.models import BaseAliquot

from edc_base.model.models import BaseUuidModel

from .aliquot_condition import AliquotCondition
from .aliquot_type import AliquotType
from .receive import Receive


class Aliquot(BaseAliquot, BaseUuidModel):
    """Stores aliquot information and is the central model in the RAORR relational model."""

    receive = models.ForeignKey(Receive, editable=False)

    aliquot_type = models.ForeignKey(AliquotType, verbose_name="Aliquot Type", null=True)

    aliquot_condition = models.ForeignKey(AliquotCondition, verbose_name="Aliquot Condition", null=True, blank=True)

    import_datetime = models.DateTimeField(null=True, editable=False)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        self.subject_identifier = self.receive.registered_subject.subject_identifier
        if self.source_aliquot and not self.primary_aliquot:
            raise ValidationError('Primary aliquot may not be None')
        super(Aliquot, self).save(*args, **kwargs)

    class Meta:
        app_label = 'lab_clinic_api'
        unique_together = (('receive', 'count'), )
        ordering = ('receive', 'count')
