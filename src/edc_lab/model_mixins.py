import re

from uuid import uuid4

from django.apps import apps as django_apps
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from edc_base.model.fields.custom_fields import InitialsField
from edc_base.model.validators import datetime_not_future
from edc_constants.choices import YES_NO
from edc_constants.constants import YES, NO
from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier
from edc_lab.site_lab_profiles import site_lab_profiles

from .constants import CONDITION_OK
from .choices import ITEM_TYPE, REASON_NOT_DRAWN, ALIQUOT_STATUS, SPECIMEN_MEASURE_UNITS, SPECIMEN_MEDIUM
from .requisition_identifier import RequisitionIdentifier

edc_device_app_config = django_apps.get_app_config('edc_device')


class AliquotModelMixin (models.Model):

    aliquot_identifier = models.CharField(
        verbose_name='Aliquot Identifier',
        max_length=25,
        unique=True,
        help_text="Aliquot identifier",
        editable=False)

    aliquot_datetime = models.DateTimeField(
        verbose_name="Date and time aliquot created",
        default=timezone.now)

    aliquot_type = models.CharField(
        verbose_name='Aliquot Type',
        validators=[RegexValidator('\d+')],
        max_length=25)

    is_primary = models.BooleanField(
        default=False,
        editable=False)

    parent_identifier = models.CharField(
        verbose_name='Parent aliquot Identifier',
        max_length=25,
        editable=False)

    specimen_identifier = models.CharField(
        verbose_name='Specimen Id',
        max_length=50,
        editable=False)

    count = models.IntegerField(
        editable=False,
        help_text='pos in sequence of aliquots from parent')

    medium = models.CharField(
        verbose_name='Medium',
        max_length=25,
        choices=SPECIMEN_MEDIUM,
        default='TUBE')

    medium_count = models.IntegerField(
        editable=False,
        default=1,
        help_text='e.g. number of tubes')

    original_measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='5.00')

    current_measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='5.00')

    measure_units = models.CharField(
        max_length=25,
        choices=SPECIMEN_MEASURE_UNITS,
        default='mL')

    status = models.CharField(
        max_length=25,
        choices=ALIQUOT_STATUS,
        default='available')

    comment = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    def __str__(self):
        return '%s' % (self.aliquot_identifier)

    def natural_key(self):
        return (self.aliquot_identifier,)

    class Meta:
        abstract = True


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

#     study_site = models.CharField(
#         max_length=10)

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
            raise RequisitionError(
                'Undefined panel name. Got {}. See AppConfig. Got {}'.format(self.panel_name, str(e)))
        self.update_requisition_identifier()
        super(RequisitionModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.requisition_identifier,)

    def update_requisition_identifier(self):
        """Converts from uuid to a requisition identifier if is_drawn == YES and not already
        a requisition identifier.

        Called from the signal."""
        pattern = re.compile(
            '^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$', re.IGNORECASE)
        if self.is_drawn == NO:
            self.requisition_identifier = str(uuid4())
        if self.is_drawn == YES and pattern.match(self.requisition_identifier):
            self.requisition_identifier = RequisitionIdentifier(self.__class__).identifier

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
            'panel': self.panel_name[0:21],
            'protocol': '',  # edc_base_app_config.protocol_number
            'requisition_identifier': self.requisition_identifier,
            'site': self.study_site,
            'specimen_identifier': self.specimen_identifier,
            'subject_identifier': self.subject_identifier,
            'visit': self.get_visit().appointment.visit_code,
        })
        return context

    class Meta:
        abstract = True


class SpecimenCollectionModelMixin (models.Model):

    collection_identifier = models.CharField(
        verbose_name='Collection Identifier',
        max_length=25,
        editable=False,
        unique=True)

    collection_datetime = models.DateTimeField(
        verbose_name="Date and time received",
        default=timezone.now,
        validators=[datetime_not_future, ],
        db_index=True)

    def __str__(self):
        return self.collection_identifier

    def natural_key(self):
        return (self.collection_identifier, )

    class Meta:
        abstract = True


class SpecimenCollectionItemModelMixin (models.Model):

    specimen_identifier = models.CharField(
        verbose_name='Specimen Identifier',
        max_length=25)

    collection_condition = models.CharField(
        verbose_name='Condition of specimen',
        max_length=50,
        default=CONDITION_OK)

    def natural_key(self):
        return (self.specimen_identifier, )

    class Meta:
        abstract = True


class PackingListModelMixin(models.Model):

    list_datetime = models.DateTimeField()

    list_comment = models.CharField(
        verbose_name='Instructions',
        max_length=100,
        null=True,
        blank=True)

    list_items = models.TextField(
        max_length=1000,
        help_text='List specimen_identifier\'s. One per line.')

    timestamp = models.CharField(
        max_length=35,
        null=True)

    received = models.BooleanField(
        default=False,
        help_text='Shipped items are all received at destination',
        editable=False)

    def save(self, *args, **kwargs):
        if not self.list_datetime:
            self.list_datetime = timezone.now()
        if not self.timestamp:
            self.timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
        super(PackingListModelMixin, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.timestamp

    def reference(self):
        return self.timestamp

    def natural_key(self):
        return self.timestamp

    def specimen_count(self):
        lst = filter(None, self.list_items.replace('\r', '').split('\n'))
        return len(lst)

    def view_list_items(self):
        return '<a href="/admin/{app_label}/{object_name}item/?q={pk}">{count} items</a>'.format(
            app_label=self._meta.app_label,
            object_name=self._meta.object_name.lower(),
            pk=self.id,
            count=self.specimen_count())
    view_list_items.allow_tags = True

    class Meta:
        abstract = True
        ordering = ['list_datetime', ]


class PackingListItemModelMixin(models.Model):

    requisition = models.CharField(
        max_length=36,
        null=True,
        blank=False,
        editable=False,
        help_text="pk of requisition instance")

    item_reference = models.CharField(
        max_length=25)

    item_datetime = models.DateTimeField(
        null=True,
        blank=True)

    item_description = models.TextField(
        max_length=100,
        null=True,
        blank=True)

    item_priority = models.CharField(
        max_length=35,
        choices=(('normal', 'Normal'), ('urgent', 'Urgent')),
        null=True,
        blank=False,
        help_text="")

    old_panel_id = models.CharField(max_length=50, null=True)

    received = models.BooleanField(
        default=False,
        help_text='Shipped items are all received at destination',
        editable=False)

    received_datetime = models.DateTimeField(
        null=True,
        help_text='Date and time shipped item was received at destination',
        editable=False)

    def __str__(self):
        return '{} {}'.format(self.item_reference, self.item_datetime.strftime('%Y-%m-%d'))

    def packing_list_model(self):
        for field in self._meta.fields:
            try:
                if issubclass(field.rel.to, PackingListModelMixin):
                    return (field.attname, field.rel.to)
            except:
                pass
        return (None, None)

    def view_packing_list(self):
        packing_list_field_attname, packing_list_model = self.packing_list_model()
        if packing_list_model:
            return '<a href="/admin/{app_label}/{object_name}/?q={pk}">{timestamp}</a>'.format(
                app_label=packing_list_model._meta.app_label,
                object_name=packing_list_model._meta.object_name.lower(),
                timestamp=packing_list_model.objects.get(
                    pk=getattr(self, packing_list_field_attname)).timestamp,
                pk=getattr(self, packing_list_field_attname),
            )
        else:
            return 'packing list'
    view_packing_list.allow_tags = True

    def priority(self):
        style = ''
        priority = ''
        if self.item_priority:
            priority = self.item_priority.lower()
            if priority == 'urgent':
                style = 'color:red;font-weight:700'
            if priority == 'normal':
                priority = ''
        return '<span style="{style}">{priority}</span>'.format(style=style, priority=priority)
    priority.allow_tags = True

    def specimen(self):
        return '{item_reference}<BR>{requisition}</a>'.format(item_reference=self.item_reference,
                                                              requisition=self.requisition.replace('requisition', ''))
    specimen.allow_tags = True

    def description(self):
        return self.item_description.replace(' ', '<BR>')
    description.allow_tags = True

    def get_subject_identifier(self):
        return ''

    class Meta:
        abstract = True
        ordering = ['created', ]


class DestinationModelMixin(models.Model):

    code = models.CharField(
        verbose_name='Code',
        max_length=25,
        unique=True)

    name = models.CharField(
        verbose_name='Name',
        max_length=50,
        unique=True)

    address = models.TextField(
        verbose_name='Address',
        max_length=250)

    tel = models.CharField(
        verbose_name='Telephone',
        max_length=50)

    email = models.CharField(
        verbose_name='Email',
        max_length=25)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.code, )

    def is_serialized(self):
        return False

    class Meta:
        abstract = True
        unique_together = (('code', 'name'), )


class ReceiveIdentifier(AlphanumericIdentifier):

    name = 'receiveidentifier'
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    seed = ['AAA', '0000']


class ReceiveModelMixin (models.Model):

    requisition_model_name = models.CharField(max_length=25, editable=False)

    subject_type = models.CharField(max_length=25, editable=False)

    receive_identifier = models.CharField(
        verbose_name='Receiving Identifier',
        max_length=25,
        editable=False,
        db_index=True,
        unique=True)

    requisition_identifier = models.CharField(
        verbose_name='Requisition Identifier',
        max_length=25,
        null=True,
        blank=True,
        db_index=True)

    drawn_datetime = models.DateTimeField(
        verbose_name="Date and time drawn",
        validators=[datetime_not_future, ],
        db_index=True)

    receive_datetime = models.DateTimeField(
        verbose_name="Date and time received",
        default=timezone.now,
        validators=[datetime_not_future, ],
        db_index=True)

    visit = models.CharField(
        verbose_name="Visit Code",
        max_length=25)

    clinician_initials = InitialsField()

    receive_condition = models.CharField(
        verbose_name='Condition of primary tube',
        max_length=50,
        null=True)

    import_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return self.receive_identifier

    def save(self, *args, **kwargs):
        if not self.id and not self.receive_identifier:
            self.receive_identifier = ReceiveIdentifier().identifier
        self.subject_type = self.registered_subject.subject_type
        super(ReceiveModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.receive_identifier, )

    class Meta:
        abstract = True
