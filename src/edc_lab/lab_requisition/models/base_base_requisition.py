from datetime import datetime
import re
import uuid

from django.core.exceptions import ImproperlyConfigured
from django.db import models

try:
    from edc.device.dispatch.models import BaseDispatchSyncUuidModel as BaseUuidModel
except ImportError:
    from edc.base.model.models import BaseUuidModel

from edc.base.model.fields import InitialsField
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc.core.bhp_string.classes import StringHelper
from edc_device.device import Device
from edc.lab.lab_profile.classes import site_lab_profiles

from ..choices import PRIORITY, REASON_NOT_DRAWN, ITEM_TYPE
from ..classes import RequisitionLabel
from ..managers import BaseRequisitionManager


class BaseBaseRequisition (BaseUuidModel):

    """ ..todo:: TODO: does not include additional tests """

    requisition_identifier = models.CharField(
        verbose_name='Requisition Id',
        max_length=50,
        unique=True,
        )

    requisition_datetime = models.DateTimeField(
        verbose_name='Requisition Date'
        )

    specimen_identifier = models.CharField(
        verbose_name='Specimen Id',
        max_length=50,
        null=True,
        blank=True,
        editable=False,
        unique=True,
        )

    protocol = models.CharField(
        verbose_name="Protocol Number",
        max_length=10,
        null=True,
        blank=True,
        help_text='Use three digit code e.g 041, 056, 062, etc'
        )

    site = models.ForeignKey(StudySite, null=True)

    clinician_initials = InitialsField(
        default='--',
        null=True,
        blank=True,
        )

    priority = models.CharField(
        verbose_name='Priority',
        max_length=25,
        choices=PRIORITY,
        default='normal',
        )

    is_drawn = models.CharField(
        verbose_name='Was a specimen drawn?',
        max_length=3,
        choices=YES_NO,
        default=YES,
        help_text='If No, provide a reason below'
        )

    reason_not_drawn = models.CharField(
        verbose_name='If not drawn, please explain',
        max_length=25,
        choices=REASON_NOT_DRAWN,
        null=True,
        blank=True,
        )

    drawn_datetime = models.DateTimeField(
        verbose_name='Date / Time Specimen Drawn',
        null=True,
        blank=True,
        help_text='If not drawn, leave blank. Same as date and time of finger prick in case on DBS.',
        )

    item_type = models.CharField(
        verbose_name='Item collection type',
        max_length=25,
        choices=ITEM_TYPE,
        default='tube',
        help_text=''
        )

    item_count_total = models.IntegerField(
        verbose_name='Total number of items',
        default=1,
        help_text='Number of tubes, samples, cards, etc being sent for this test/order only. Determines number of labels to print',
        )

    estimated_volume = models.DecimalField(
        verbose_name='Estimated volume in mL',
        max_digits=7,
        decimal_places=2,
        default=5.0,
        help_text='If applicable, estimated volume of sample for this test/order. This is the total volume if number of "tubes" above is greater than 1'
        )

    comments = models.TextField(
        max_length=25,
        null=True,
        blank=True,
        )

    is_receive = models.BooleanField(
        verbose_name='received',
        default=False,
        )

    is_receive_datetime = models.DateTimeField(
        verbose_name='rcv-date',
        null=True,
        blank=True,
        )

    is_packed = models.BooleanField(
        verbose_name='packed',
        default=False,
        )

    is_labelled = models.BooleanField(
        verbose_name='labelled',
        default=False,
        )

    is_labelled_datetime = models.DateTimeField(
        verbose_name='label-date',
        null=True,
        blank=True,
        )

    is_lis = models.BooleanField(
        verbose_name='lis',
        default=False,
        )

    objects = BaseRequisitionManager()

    def __unicode__(self):
        return '%s' % (self.requisition_identifier)

    def get_visit(self):
        raise ImproperlyConfigured('Method must be overridden')

    # TODO: remove this, should be get_subject_identifier
    def get_infant_identifier(self):
        return self.get_visit().appointment.registered_subject.subject_identifier

    # TODO: remove this, should be get_subject_identifier
    def subject(self):
        return self.get_subject_identifier()

    @property
    def report_datetime(self):
        return self.requisition_datetime

    def visit(self):
        return self.get_visit().appointment.visit_definition.code

    def get_subject_identifier(self):
        return self.get_visit().appointment.registered_subject.subject_identifier

    def barcode_value(self):
        return self.specimen_identifier

    def natural_key(self):
        return (self.requisition_identifier, )

    def save(self, *args, **kwargs):
        if self.is_drawn.lower() == YES and not self.value_is_requisition_identifier():
            self.requisition_identifier = self.prepare_requisition_identifier()
        if self.is_drawn.lower() == NO and not self.value_is_uuid():
            self.requisition_identifier = str(uuid.uuid4())
        return super(BaseBaseRequisition, self).save(*args, **kwargs)

    def value_is_requisition_identifier(self):
        if not self.requisition_identifier:
            return False
        if len(self.requisition_identifier) == 7:
            return True
        return False

    def value_is_uuid(self):
        p = re.compile('^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$', re.IGNORECASE)
        if not self.requisition_identifier:
            return False
        if len(self.requisition_identifier) == 36 and p.match(self.requisition_identifier):
            return True
        return False

    def get_site_code(self):
        site_code = ''
        try:
            site_code = self.site.site_code
        except AttributeError:
            raise ImproperlyConfigured(
                'Site may not be None. Either include the field for user input or '
                'override method get_site_code() on the concrete model.')
        return site_code

    def prepare_requisition_identifier(self, **kwargs):
        """Generate and returns a locally unique requisition identifier for a device (adds device id)"""
        device = Device()
        device_id = kwargs.get('device_id', device.device_id)
        string = StringHelper()
        length = 5
        template = '{device_id}{random_string}'
        opts = {'device_id': device_id, 'random_string': string.get_safe_random_string(length=length)}
        requisition_identifier = template.format(**opts)
        # look for a duplicate
        if self.__class__.objects.filter(requisition_identifier=requisition_identifier):
            n = 1
            while self.__class__.objects.filter(requisition_identifier=requisition_identifier):
                requisition_identifier = template.format(**opts)
                n += 1
                if n == len(string.safe_allowed_chars) ** length:
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
            self.modified = datetime.today()
            self.save(update_fields=['is_labelled', 'modified'])

    class Meta:
        abstract = True
