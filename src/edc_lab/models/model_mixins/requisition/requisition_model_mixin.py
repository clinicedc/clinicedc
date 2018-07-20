from django.db import models
from django.utils import timezone
from edc_model_fields.fields import OtherCharField, InitialsField
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE

from ....choices import ITEM_TYPE, REASON_NOT_DRAWN
from ..panel_model_mixin import PanelModelMixin
from .requisition_verify_model_mixin import RequisitionVerifyModelMixin


class RequisitionModelMixin(PanelModelMixin, SiteModelMixin,
                            RequisitionVerifyModelMixin, models.Model):

    requisition_datetime = models.DateTimeField(
        default=timezone.now,
        verbose_name='Requisition Date')

    drawn_datetime = models.DateTimeField(
        verbose_name='Date / Time Specimen Drawn',
        null=True,
        blank=True,
        help_text=(
            'If not drawn, leave blank. Same as date and time of '
            'finger prick in case on DBS.'))

    is_drawn = models.CharField(
        verbose_name='Was a specimen drawn?',
        max_length=3,
        choices=YES_NO,
        help_text='If No, provide a reason below')

    reason_not_drawn = models.CharField(
        verbose_name='If not drawn, please explain',
        max_length=25,
        default=NOT_APPLICABLE,
        choices=REASON_NOT_DRAWN)

    reason_not_drawn_other = OtherCharField()

    protocol_number = models.CharField(
        max_length=10,
        null=True,
        editable=False)

    clinician_initials = InitialsField(
        null=True,
        blank=True)

    specimen_type = models.CharField(
        verbose_name='Specimen type',
        max_length=25,
        null=True,
        blank=True)

    item_type = models.CharField(
        verbose_name='Item collection type',
        max_length=25,
        choices=ITEM_TYPE,
        default=NOT_APPLICABLE,
        help_text='')

    item_count = models.IntegerField(
        verbose_name='Number of items',
        null=True,
        blank=True,
        help_text=(
            'Number of tubes, samples, cards, etc being sent for this test/order only. '
            'Determines number of labels to print'))

    estimated_volume = models.DecimalField(
        verbose_name='Estimated volume in mL',
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            'If applicable, estimated volume of sample for this test/order. '
            'This is the total volume if number of "tubes" above is greater than 1'))

    comments = models.TextField(
        max_length=25,
        null=True,
        blank=True)

    def save(self, *args, **kwargs):
        self.specimen_type = self.panel_object.aliquot_type.alpha_code
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.requisition_identifier, )
    natural_key.dependencies = ['sites.Site']

    class Meta:
        abstract = True
