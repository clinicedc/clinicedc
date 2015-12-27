import re

from uuid import uuid4

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.utils.translation import ugettext as _

from edc.core.bhp_variables.models import StudySite
from edc_base.audit_trail import AuditTrail
from edc_base.encrypted_fields import (
    IdentityField, EncryptedCharField, FirstnameField, LastnameField, mask_encrypted)
from edc_base.model.fields import IdentityTypeField
from edc_base.model.fields.custom_fields import IsDateEstimatedField
from edc_base.model.models.base_uuid_model import BaseUuidModel
from edc_constants.choices import YES_NO, POS_NEG_UNKNOWN, ALIVE_DEAD_UNKNOWN
from edc_sync.models import SyncModelMixin

# try:
#     from edc.device.dispatch.models import BaseDispatchSyncUuidModel
#
#     class BaseRegisteredSubject(Subject, BaseDispatchSyncUuidModel):
#         class Meta:
#             abstract = True
# except ImportError:
#     class BaseRegisteredSubject(Subject):
#         class Meta:
#             abstract = True


class RegisteredSubjectError(Exception):
    pass


class RegisteredSubjectManager(models.Manager):

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class RegisteredSubject(SyncModelMixin, BaseUuidModel):

    max_subjects = None

    subject_types = None

    def __init__(self, *args, **kwargs):
        self.max_subjects = settings.MAX_SUBJECTS
        self.subject_types = settings.SUBJECT_TYPES
        for subject_type in self.subject_types:
            try:
                self.max_subjects[subject_type]
            except KeyError as e:
                RegisteredSubjectError('Expected enrollment cap for {}. Got {}'.format(subject_type, str(e)))
        super(RegisteredSubject, self).__init__(*args, **kwargs)

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        blank=True,
        db_index=True,
        unique=True)

    subject_identifier_as_pk = models.CharField(
        verbose_name="Subject Identifier as pk",
        max_length=50,
        null=True,
        db_index=True,
    )

    subject_identifier_aka = models.CharField(
        verbose_name="Subject Identifier a.k.a",
        max_length=50,
        null=True,
        editable=False,
        help_text='track a previously allocated identifier.'
    )

    dm_comment = models.CharField(
        verbose_name="Data Management comment",
        max_length=150,
        null=True,
        editable=False,
        help_text='see also edc.data manager.'
    )

    # may not be available when instance created (e.g. infants prior to birth report)
    first_name = FirstnameField(
        null=True,
    )

    # may not be available when instance created (e.g. infants or household subject before consent)
    last_name = LastnameField(
        verbose_name="Last name",
        null=True,
    )

    # may not be available when instance created (e.g. infants)
    initials = EncryptedCharField(
        validators=[RegexValidator(
            regex=r'^[A-Z]{2,3}$',
            message=('Ensure initials consist of letters '
                     'only in upper case, no spaces.'))],
        null=True,
    )

    dob = models.DateField(
        verbose_name=_("Date of birth"),
        null=True,
        blank=False,
        help_text=_("Format is YYYY-MM-DD"),
    )

    is_dob_estimated = IsDateEstimatedField(
        verbose_name=_("Is date of birth estimated?"),
        null=True,
        blank=False,
    )

    gender = models.CharField(
        verbose_name="Gender",
        max_length=1,
        null=True,
        blank=False,
    )

    subject_type = models.CharField(
        max_length=25)

    subject_consent_id = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    registration_identifier = models.CharField(
        max_length=36,
        null=True,
        blank=True)

    sid = models.CharField(
        verbose_name="SID",
        max_length=15,
        null=True,
        blank=True)

    study_site = models.ForeignKey(
        StudySite,
        verbose_name='Site',
        help_text="",
        null=True,
        blank=True)

    relative_identifier = models.CharField(
        verbose_name="Identifier of immediate relation",
        max_length=25,
        null=True,
        blank=True,
        help_text="For example, mother's identifier, if available / appropriate")

    identity = IdentityField(
        null=True,
        blank=True)

    identity_type = IdentityTypeField()

    may_store_samples = models.CharField(
        verbose_name=_("Sample storage"),
        max_length=3,
        choices=YES_NO,
        default='?',
        help_text=_("Does the subject agree to have samples stored after the study has ended"))

    hiv_status = models.CharField(
        verbose_name='Hiv status',
        max_length=15,
        choices=POS_NEG_UNKNOWN,
        null=True,
        blank=True)

    survival_status = models.CharField(
        verbose_name='Survival status',
        max_length=15,
        choices=ALIVE_DEAD_UNKNOWN,
        null=True,
        blank=True)

    screening_identifier = models.CharField(
        max_length=36,
        null=True,
        blank=True)

    screening_datetime = models.DateTimeField(
        null=True,
        blank=True)

    screening_age_in_years = models.IntegerField(
        null=True,
        blank=True)

    registration_datetime = models.DateTimeField(
        null=True,
        blank=True)

    """ for simplicity, if going straight from screen to rando,
        update both registration date and randomization date """
    randomization_datetime = models.DateTimeField(
        null=True,
        blank=True)

    registration_status = models.CharField(
        verbose_name="Registration status",
        max_length=25,
        null=True,
        blank=True)

    comment = models.TextField(
        verbose_name='Comment',
        max_length=250,
        null=True,
        blank=True)

    additional_key = models.CharField(
        max_length=36,
        verbose_name='-',
        editable=False,
        default=None,
        null=True,
        help_text=('A uuid (or some other text value) to be added to bypass the '
                   'unique constraint of just firstname, initials, and dob.'
                   'The default constraint proves limiting since the source model usually has some other'
                   'attribute in additional to first_name, initials and dob which '
                   'is not captured in this model'))

    # not used: this field should be removed
    salt = models.CharField(max_length=25, null=True, editable=False, default='salt')

    objects = RegisteredSubjectManager()

    history = AuditTrail()

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        self.check_max_subjects()
        if self.identity:
            self.additional_key = None
        self.set_uuid_as_subject_identifier_if_none()
        self.raise_on_duplicate_subject_identifier(using)
        self.raise_on_changed_subject_identifier(using)
        super(RegisteredSubject, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier_as_pk, )

    def __unicode__(self):
        return "{subject_identifier} {subject_type} ({first_name} {initials}){sid}".format(
            subject_identifier=self.mask_unset_subject_identifier(),
            subject_type=self.subject_type,
            first_name=mask_encrypted(self.first_name),
            initials=self.initials,
            sid=' sid={}'.format(self.sid) if self.sid else '')

    def mask_subject_identifier(self):
        subject_identifier = self.subject_identifier
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        if re_pk.match(subject_identifier):
            subject_identifier = '<identifier not set>'
        return subject_identifier

    def raise_on_changed_subject_identifier(self, using):
        if self.id:
            with transaction.atomic():
                obj = self.__class__.objects.get(pk=self.id)
                if obj.subject_identifier != self.subject_identifier_as_pk:
                    if self.subject_identifier != obj.subject_identifier:
                        raise RegisteredSubjectError(
                            'Subject identifier cannot be changed for existing registered subject. '
                            'Got {}.'.format(self.subject_identifier))

    def raise_on_duplicate_subject_identifier(self, using):
        """Checks if the subject identifier is in use, for new and existing instances."""
        with transaction.atomic():
            error_msg = (
                'Attempt to insert or update duplicate value for subject_identifier {0} '
                'when saving {1} '.format(self.subject_identifier, self))
            try:
                obj = self.__class__.objects.using(using).get(
                    subject_identifier=self.subject_identifier)
                if obj.id != self.id:
                    raise RegisteredSubjectError(error_msg)
            except self.__class__.DoesNotExist:
                pass
            except MultipleObjectsReturned:
                raise RegisteredSubjectError(error_msg)

    def set_uuid_as_subject_identifier_if_none(self):
        """Inserts a random uuid as a dummy identifier for a new instance.

        Model uses subject_identifier_as_pk as a natural key for
        serialization/deserialization. Value must not change once set."""
        if not self.subject_identifier_as_pk:
            self.subject_identifier_as_pk = str(uuid4())  # this will never change
            if not self.subject_identifier:
                self.subject_identifier = self.subject_identifier_as_pk

    def check_max_subjects(self, exception_cls=None, settings_attrs=None, count=None):
        """Checks the number of subjects against the settings attribute MAX_SUBJECTS.

        Format is MAX_SUBJECTS = {'maternal': 1000, 'infant': 1500}.

        For testing, you can skip these verifications by using 'test_subject_type' as the subject_type."""
        exception_cls = exception_cls or ValidationError
        if not settings_attrs:
            settings_attrs = settings
        if not self.id:
            max_subjects = self.max_subjects.get(self.subject_type)
            if not count:
                count = self.__class__.objects.filter(subject_type=self.get_subject_type(settings_attrs)).count()
            if count + 1 > max_subjects:
                raise exception_cls(
                    ('Maximum number of subjects has been reached for subject_type {0}. '
                     'Got {1}/{2}.').format(self.get_subject_type(settings_attrs), count, max_subjects))

    def verify_settings_attr(self, settings_attrs=None):
        """Verify that attribute SUBJECT_TYPES exists, at least.

        For testing, you can skip these verifications by using 'test_subject_type' as the subject_type."""
        if not settings_attrs:
            settings_attrs = settings
        if 'SUBJECT_TYPES' not in dir(settings_attrs):
            raise ImproperlyConfigured('Missing settings attribute. Required list SUBJECT_TYPES. '
                                       'e.g SUBJECT_TYPES = [\'maternal\', \'infant\'].')
        if 'MAX_SUBJECTS' in dir(settings_attrs):
            if not isinstance(settings_attrs.MAX_SUBJECTS, dict):
                raise ImproperlyConfigured('Setting attribute MAX_SUBJECTS must be a dictionary of format '
                                           'MAX_SUBJECTS = {{\'maternal\': 1000, \'infant\': 1500, ...}}. '
                                           'Got {0}.'.format(settings_attrs.MAX_SUBJECTS))
            if not self.get_subject_type(settings_attrs).lower() in settings_attrs.MAX_SUBJECTS.keys():
                raise ImproperlyConfigured('Setting attribute MAX_SUBJECTS should be a dictionary with a '
                                           'key for subject_type {0}. Got {1}.'.format(
                                               self.get_subject_type(settings_attrs), settings_attrs.MAX_SUBJECTS))
            if not filter(lambda n: isinstance(n, int), settings_attrs.MAX_SUBJECTS.values()):
                raise ImproperlyConfigured('Setting attribute dictionary MAX_SUBJECTS must return an integer '
                                           'for each value. Got {0}.'.format(settings_attrs.MAX_SUBJECTS))

    def get_registered_subject(self):
        return self

    def get_subject_types(self, settings_attrs=None):
        if not settings_attrs:
            settings_attrs = settings
        settings_attrs.SUBJECT_TYPES.append('test_subject_type')  # added for tests
        return map(lambda n: n.lower(), settings_attrs.SUBJECT_TYPES)

    def get_subject_type(self, settings_attrs=None):
        if not settings_attrs:
            settings_attrs = settings
        if not self.subject_type:
            raise TypeError('subject_type may not be None for model class {0} instance {1}.'.format(
                self.__class__, self))
        if self.subject_type.lower() not in self.get_subject_types(settings_attrs):
            raise TypeError('Expected subject_type to be any of {0}. Got \'{1}\'. Either update the settings '
                            'attribute in settings.py or change the subject_type of the registered_subject.'.format(
                                self.get_subject_types(settings_attrs), self.subject_type))
        return self.subject_type

    def check_if_may_change_subject_identifier(self, using):
        """Allows a consent to change the subject identifier."""
        pass

    def get_subject_identifier(self):
        return self.subject_identifier

    def include_for_dispatch(self):
        return True

    def is_serialized(self):
        return super(RegisteredSubject, self).is_serialized(True)

    def dispatch_container_lookup(self):
        return (self.__class__, 'id')

    def is_dispatched(self):
        return False

    def is_dispatchable_model(self):
        return True

    def bypass_for_edit_dispatched_as_item(self, using=None, update_fields=None):
        # requery myself
        obj = self.__class__.objects.using(using).get(pk=self.pk)
        # dont allow values in these fields to change if dispatched
        may_not_change_these_fields = [
            (k, v) for k, v in obj.__dict__.iteritems()
            if k not in ['study_site_id', 'registration_status', 'modified'] and not k.startswith('_')]
        for k, v in may_not_change_these_fields:
            if getattr(self, k) != v:
                return False
        return True

    def age(self):
        return self.screening_age_in_years
    age.allow_tags = True

    def dashboard(self):
        ret = None
        if self.subject_identifier:
            url = reverse('subject_dashboard_url', kwargs={
                'dashboard_type': self.subject_type.lower(),
                'dashboard_id': self.pk,
                'dashboard_model': 'registered_subject',
                'show': 'appointments'})
            ret = """<a href="{url}" />dashboard</a>""".format(url=url)
        return ret
    dashboard.allow_tags = True

    class Meta:
        app_label = 'registration'
        db_table = 'bhp_registration_registeredsubject'
        verbose_name = 'Registered Subject'
        ordering = ['subject_identifier']
        unique_together = ('first_name', 'dob', 'initials', 'additional_key')
