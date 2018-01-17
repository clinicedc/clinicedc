from django.db import models
from django.utils import timezone

from edc_base.model_fields import InitialsField
from edc_base.model_fields.custom_fields import OtherCharField
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_constants.choices import YES_NO
from edc_constants.constants import YES, NOT_APPLICABLE

from ....choices import ITEM_TYPE, REASON_NOT_DRAWN
from ..panel_model_mixin import PanelModelMixin


class RequisitionModelMixin(PanelModelMixin, SiteModelMixin, models.Model):

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
        default=YES,
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
        return (self.requisition_identifier,)

    def label_context(self, extra_context=None):
        context = {}
        may_store_samples = None
        context.update({
            'aliquot_count': 1,
            'aliquot_type': self.aliquot_type.alpha_code.upper(),
            'barcode_value': self.barcode_value(),
            'clinician_initials': self.user_created[0:2].upper(),
            'dob': self.registered_subject.dob,
            'drawn_datetime': self.drawn_datetime,
            'gender': self.registered_subject.gender,
            'initials': self.registered_subject.initials,
            'item_count': self.item_count,
            'may_store_samples': may_store_samples,
            'panel': self.panel.verbose_name[0:21],
            'protocol': '',  # edc_base_app_config.protocol_number
            'requisition_identifier': self.requisition_identifier,
            'site': self.study_site,
            'subject_identifier': self.subject_identifier,
            'visit': self.get_visit().appointment.visit_code,
        })
        return context

    class Meta:
        abstract = True
