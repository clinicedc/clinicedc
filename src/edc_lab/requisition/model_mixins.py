import re
import random
from uuid import uuid4

from django.apps import apps as django_apps
from django.core.urlresolvers import reverse
from django.db import models

from edc_base.model.fields.custom_fields import InitialsField
from edc_constants.choices import YES_NO
from edc_constants.constants import YES, NO

from .choices import ITEM_TYPE, REASON_NOT_DRAWN
from .identifier import Identifier
from edc_lab.site_lab_profiles import site_lab_profiles

app_confi = django_apps.get_app_config('edc_lab')
edc_device_app_config = django_apps.get_app_config('edc_device')


class RequisitionError(Exception):
    pass


class RequisitionModelMixin(models.Model):

    panel_name = models.CharField(
        max_length=25)

    requisition_identifier = models.CharField(
        verbose_name='Requisition Id',
        max_length=50,
        unique=True,
        editable=False)

    requisition_datetime = models.DateTimeField(
        verbose_name='Requisition Date')

    drawn_datetime = models.DateTimeField(
        verbose_name='Date / Time Specimen Drawn',
        null=True,
        blank=True,
        help_text=(
            'If not drawn, leave blank. Same as date and time of finger prick in case on DBS.'))

    is_drawn = models.CharField(
        verbose_name='Was a specimen drawn?',
        max_length=3,
        choices=YES_NO,
        default=YES,
        help_text='If No, provide a reason below')

    reason_not_drawn = models.CharField(
        verbose_name='If not drawn, please explain',
        max_length=25,
        choices=REASON_NOT_DRAWN,
        null=True,
        blank=True,)

    study_site = models.CharField(
        max_length=10)

    specimen_identifier = models.CharField(
        verbose_name='Specimen Id',
        max_length=50,
        null=True,
        editable=False,
        unique=True)

    study_site = models.CharField(max_length=10, null=True)

    clinician_initials = InitialsField(
        null=True,
        blank=True)

    specimen_type = models.CharField(
        verbose_name='Specimen type',
        max_length=25)

    item_type = models.CharField(
        verbose_name='Item collection type',
        max_length=25,
        choices=ITEM_TYPE,
        default='tube',
        help_text='')

    item_count = models.IntegerField(
        verbose_name='Number of items',
        default=1,
        help_text=(
            'Number of tubes, samples, cards, etc being sent for this test/order only. '
            'Determines number of labels to print'))

    estimated_volume = models.DecimalField(
        verbose_name='Estimated volume in mL',
        max_digits=7,
        decimal_places=2,
        default=5.0,
        help_text=(
            'If applicable, estimated volume of sample for this test/order. '
            'This is the total volume if number of "tubes" above is greater than 1'))

    comments = models.TextField(
        max_length=25,
        null=True,
        blank=True)

    def save(self, *args, **kwargs):
        if not self.requisition_identifier:
            self.requisition_identifier = str(uuid4())
        try:
            site_lab_profiles.get(self._meta.label_lower).panels[self.panel_name]
        except KeyError as e:
            raise RequisitionError('Undefined panel name. Got {}. See AppConfig. Got {}'.format(self.panel_name, str(e)))
        super(RequisitionModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.requisition_identifier,)

    def update_requisition_identifier(self, sender):
        """Converts from uuid to a requisition identifier if is_drawn == YES and not already
        a requisition identifier.

        Called from the signal."""
        pattern = re.compile(
            '^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$', re.IGNORECASE)
        if self.is_drawn == NO:
            self.requisition_identifier = str(uuid4())
        if self.is_drawn == YES and pattern.match(self.requisition_identifier):
            self.requisition_identifier = Identifier(sender).identifier

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
            'panel': self.panel.name[0:21],
            'protocol': '',  # edc_base_app_config.protocol_number
            'requisition_identifier': self.requisition_identifier,
            'site': self.study_site,
            'specimen_identifier': self.specimen_identifier,
            'subject_identifier': self.subject_identifier,
            'visit': self.get_visit().appointment.visit_code,
        })
        return context

    # begin model methods for admin ---------------------
    def aliquot(self):
        url = reverse('admin:{}_{}_changelist'.format(
            self.aliquot_model._meta.app_label,
            self.aliquot_model._meta.model_name.lower()))
        return """<a href="{url}?q={requisition_identifier}" />aliquot</a>""".format(
            url=url, requisition_identifier=self.requisition_identifier)
    aliquot.allow_tags = True

    def subject(self):
        return self.subject_identifier
    subject.allow_tags = True

#     def visit(self):
#         visit = getattr(self, self.visit_model_attr)
#         url = reverse('admin:{}_{}_changelist'.format(
#             self.visit_model._meta.app_label,
#             self.visit_model._meta.model_name.lower()))
#         return """<a href="{url}?q={pk}" />{code}.{instance}</a>""".format(
#             url=url,
#             pk=getattr(self, self.visit_model_attr).pk,
#             code=visit.appointment.visit_definition.code,
#             instance=visit.appointment.visit_instance)
#     visit.allow_tags = True
#     # end model methods for admin ---------------------

    class Meta:
        abstract = True
