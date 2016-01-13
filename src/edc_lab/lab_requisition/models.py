import re

import random
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from edc_identifier.old_identifier import Identifier

from edc_base.model.fields.custom_fields import InitialsField
from edc_constants.choices import YES_NO
from edc_constants.constants import YES, NO
from edc_device import Device
from edc_lab.lab_clinic_api.models import TestCode

from .choices import ITEM_TYPE, REASON_NOT_DRAWN, PRIORITY
from .classes import RequisitionLabel


class RequisitionManager(models.Manager):

    def get_by_natural_key(self, requisition_identifier):
        return self.get(requisition_identifier=requisition_identifier)

    def get_global_identifier(self, **kwargs):
        """Generates and returns a globally unique requisition identifier
        (adds site and protocolnumber)"""
        device = Device()
        if not device.is_server:
            raise ValueError(
                'Only SERVERs may access method \'get_global_identifier\' machine_type.')
        identifier = Identifier(
            subject_type='specimen',
            site_code=kwargs.get('site_code', settings.SITE_CODE),
            protocol_code=kwargs.get('protocol_code', settings.PROTOCOL_NUMBER),
            counter_length=4)
        identifier.create()

        return identifier


class RequisitionModelMixin(models.Model):

    def __init__(self, *args, **kwargs):
        if not self.aliquot_model:
            raise ImproperlyConfigured('{}.aliquot model cannot be None'.format(self.__class__.__name__))
        super(RequisitionModelMixin, self).__init__(*args, **kwargs)

    aliquot_model = None

    # populate this one based on the selected panel at the dashboard
    test_code = models.ManyToManyField(
        TestCode,
        verbose_name='Additional tests',
        null=True,
        blank=True)

    subject_identifier = models.CharField(
        max_length=25,
        null=True,
        editable=False)

    requisition_identifier = models.CharField(
        verbose_name='Requisition Id',
        max_length=50,
        unique=True,)

    requisition_datetime = models.DateTimeField(
        verbose_name='Requisition Date')

    specimen_identifier = models.CharField(
        verbose_name='Specimen Id',
        max_length=50,
        null=True,
        blank=True,
        editable=False,
        unique=True,)

    protocol = models.CharField(
        verbose_name="Protocol Number",
        max_length=10,
        null=True,
        blank=True,
        help_text='Use three digit code e.g 041, 056, 062, etc')

    study_site = models.CharField(max_length=10, null=True)

    clinician_initials = InitialsField(
        default='--',
        null=True,
        blank=True,)

    priority = models.CharField(
        verbose_name='Priority',
        max_length=25,
        choices=PRIORITY,
        default='normal',)

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

    drawn_datetime = models.DateTimeField(
        verbose_name='Date / Time Specimen Drawn',
        null=True,
        blank=True,
        help_text=(
            'If not drawn, leave blank. Same as date and time of finger prick in case on DBS.'))

    item_type = models.CharField(
        verbose_name='Item collection type',
        max_length=25,
        choices=ITEM_TYPE,
        default='tube',
        help_text='')

    item_count_total = models.IntegerField(
        verbose_name='Total number of items',
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
        blank=True,)

    is_receive = models.BooleanField(
        verbose_name='received',
        default=False,)

    is_receive_datetime = models.DateTimeField(
        verbose_name='rcv-date',
        null=True,
        blank=True,)

    is_packed = models.BooleanField(
        verbose_name='packed',
        default=False,)

    is_labelled = models.BooleanField(
        verbose_name='labelled',
        default=False,)

    is_labelled_datetime = models.DateTimeField(
        verbose_name='label-date',
        null=True,
        blank=True,)

    is_lis = models.BooleanField(
        verbose_name='lis',
        default=False,)

    def save(self, *args, **kwargs):
        self.subject_identifier = self.get_visit().get_subject_identifier()
        if self.is_drawn == YES and not self.value_is_requisition_identifier():
            self.requisition_identifier = self.prepare_requisition_identifier()
        if self.is_drawn == NO and not self.value_is_uuid():
            self.requisition_identifier = str(uuid4())
        super(RequisitionModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.requisition_identifier,)

    def barcode_value(self):
        return self.specimen_identifier

    def value_is_requisition_identifier(self):
        if not self.requisition_identifier:
            return False
        if len(self.requisition_identifier) == 7:
            return True
        return False

    def value_is_uuid(self):
        p = re.compile(
            '^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$', re.IGNORECASE)
        if not self.requisition_identifier:
            return False
        if (len(self.requisition_identifier) == 36 and p.match(self.requisition_identifier)):
            return True
        return False

    def prepare_requisition_identifier(self, **kwargs):
        """Generate and returns a locally unique requisition
        identifier for a device (adds device id)"""
        device = Device()
        device_id = kwargs.get('device_id', device.device_id)
        template = '{device_id}{random_string}'
        opts = {
            'device_id': device_id,
            'random_string': ''.join([random.choice('ABCDEFGHKMNPRTUVWXYZ2346789') for _ in range(5)])}
        requisition_identifier = template.format(**opts)
        # look for a duplicate
        if self.__class__.objects.filter(requisition_identifier=requisition_identifier):
            n = 1
            while self.__class__.objects.filter(requisition_identifier=requisition_identifier):
                requisition_identifier = template.format(**opts)
                n += 1
                if n == len('ABCDEFGHKMNPRTUVWXYZ2346789') ** 5:
                    raise TypeError('Unable prepare a unique requisition identifier, '
                                    'all are taken. Increase the length of the random string')
        return requisition_identifier

    def print_label(self, request):
        """ Prints a label flags this requisition as 'labeled'.

        Uses :func:`print label` method on the :class:`RequisitionLabel` class.

        If the specimen identifier is not set, the label will not print."""
        if self.specimen_identifier:
            requisition_label = RequisitionLabel()
            requisition_label.print_label(request, self, self.item_count_total)
            self.is_labelled = True
            self.modified = timezone.now()
            self.save(update_fields=['is_labelled', 'modified'])

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

    def visit(self):
        visit = getattr(self, self.visit_model_attr)
        url = reverse('admin:{}_{}_changelist'.format(
            self.visit_model._meta.app_label,
            self.visit_model._meta.model_name.lower()))
        return """<a href="{url}?q={pk}" />{code}.{instance}</a>""".format(
            url=url,
            pk=getattr(self, self.visit_model_attr).pk,
            code=visit.appointment.visit_definition.code,
            instance=visit.appointment.visit_instance)
    visit.allow_tags = True

    class Meta:
        abstract = True
