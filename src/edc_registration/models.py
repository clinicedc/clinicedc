import re

from uuid import uuid4

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django_crypto_fields.fields import (
    IdentityField, EncryptedCharField, FirstnameField, LastnameField)
from django_crypto_fields.mask_encrypted import mask_encrypted
from simple_history.models import HistoricalRecords as AuditTrail

from edc_base.model.fields import IdentityTypeField
from edc_base.model.fields.custom_fields import IsDateEstimatedField
from edc_constants.choices import YES_NO, POS_NEG_UNKNOWN, ALIVE_DEAD_UNKNOWN


class RegisteredSubjectError(Exception):
    pass


class RegisteredSubjectManager(models.Manager):

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class RegisteredSubjectModelMixin(models.Model):

    max_subjects = None

    subject_types = None

    def __init__(self, *args, **kwargs):
        try:
            self.subject_types = settings.SUBJECT_TYPES
        except AttributeError:
            self.subject_types = ['subject']
        try:
            self.max_subjects = settings.MAX_SUBJECTS
        except AttributeError as e:
            if self.subject_types == ['subject']:
                self.max_subjects = {'subject': -1}
            else:
                raise AttributeError(str(e))
        for subject_type in self.subject_types:
            try:
                self.max_subjects[subject_type]
            except KeyError as e:
                raise RegisteredSubjectError(
                    'Expected enrollment cap for \'{}\'. See settings.MAX_SUBJECTS.'.format(subject_type))
            except TypeError as e:
                raise RegisteredSubjectError(
                    'Expected a dictionary for settings.MAX_SUBJECTS. Got {}'.format(str(e)))
        super(RegisteredSubjectModelMixin, self).__init__(*args, **kwargs)

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

    # may not be available when instance created (e.g. infants prior to birth report)
    first_name = FirstnameField(
        null=True,
    )

    # may not be available when instance created (e.g. infants or household subject before consent)
    last_name = LastnameField(
        verbose_name="Last name",
        null=True)

    # may not be available when instance created (e.g. infants)
    initials = EncryptedCharField(
        validators=[RegexValidator(
            regex=r'^[A-Z]{2,3}$',
            message=('Ensure initials consist of letters '
                     'only in upper case, no spaces.'))],
        null=True)

    dob = models.DateField(
        verbose_name=_("Date of birth"),
        null=True,
        blank=False,
        help_text=_("Format is YYYY-MM-DD"))

    is_dob_estimated = IsDateEstimatedField(
        verbose_name=_("Is date of birth estimated?"),
        null=True,
        blank=False)

    gender = models.CharField(
        verbose_name="Gender",
        max_length=1,
        null=True,
        blank=False)

    subject_type = models.CharField(
        max_length=25,
        default='subject')

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

    study_site = models.CharField(
        max_length=50,
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

    dm_comment = models.CharField(
        verbose_name="Data Management comment",
        max_length=150,
        null=True,
        editable=False)

    objects = RegisteredSubjectManager()

    history = AuditTrail()

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        self.raise_on_unknown_subject_type()
        self.raise_on_max_subjects()
        if self.identity:
            self.additional_key = None
        self.set_uuid_as_subject_identifier_if_none()
        self.raise_on_duplicate_subject_identifier(using)
        self.raise_on_changed_subject_identifier(using)
        super(RegisteredSubjectModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier_as_pk, )

    def __str__(self):
        return "{subject_identifier} {subject_type} ({first_name} {initials}){sid}".format(
            subject_identifier=self.mask_subject_identifier(),
            subject_type=self.subject_type,
            first_name=mask_encrypted(self.first_name),
            initials=self.initials,
            sid=' sid={}'.format(self.sid) if self.sid else '')

    def mask_subject_identifier(self):
        if not self.subject_identifier_is_set():
            return '<identifier not set>'
        return self.subject_identifier

    def subject_identifier_is_set(self):
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        if re_pk.match(self.subject_identifier):
            return False
        return True

    def raise_on_changed_subject_identifier(self, using):
        """Raises an exception if there is an attempt to change the subject identifier
        for an existing instance if the subject identifier is already set."""
        if self.id and self.subject_identifier_is_set():
            with transaction.atomic():
                obj = self.__class__.objects.get(pk=self.id)
                if obj.subject_identifier != self.subject_identifier_as_pk:
                    if self.subject_identifier != obj.subject_identifier:
                        raise RegisteredSubjectError(
                            'Subject identifier cannot be changed for existing registered subject. '
                            'Got {} <> {}.'.format(self.subject_identifier, obj.subject_identifier))

    def raise_on_duplicate_subject_identifier(self, using):
        """Checks if the subject identifier is in use, for new and existing instances."""
        with transaction.atomic():
            error_msg = (
                'Cannot {{action}} registered subject with a duplicate '
                'subject_identifier. Got {0}.'.format(self.subject_identifier))
            try:
                obj = self.__class__.objects.using(using).get(
                    subject_identifier=self.subject_identifier)
                if not self.id:
                    raise RegisteredSubjectError(error_msg.format(action='insert'))
                elif self.subject_identifier_is_set() and obj.id != self.id:
                    raise RegisteredSubjectError(error_msg.format(action='update'))
            except self.__class__.DoesNotExist:
                pass

    def raise_on_unknown_subject_type(self):
        if self.subject_type not in self.subject_types:
            raise RegisteredSubjectError(
                'Subject type must be one of {}. Got {}.'.format(self.subject_types, self.subject_type))

    def raise_on_max_subjects(self, exception_cls=None):
        """Raises an exception if the maximum number enrollees of
        'subject_type' has been reached.

        Note: a value of -1 means registration is unlimited for the subject_type"""

        exception_cls = exception_cls or RegisteredSubjectError
        if not self.id:
            max_subject = self.max_subjects.get(self.subject_type)
            if max_subject >= 0:
                count = self.__class__.objects.filter(subject_type=self.subject_type).count()
                if count >= max_subject:
                    raise exception_cls(
                        'Maximum number of subjects has been reached for subject_type \'{}\'. '
                        'Maximum allowed is {}.'.format(self.subject_type, count, max_subject))

    def set_uuid_as_subject_identifier_if_none(self):
        """Inserts a random uuid as a dummy identifier for a new instance.

        Model uses subject_identifier_as_pk as a natural key for
        serialization/deserialization. Value must not change once set."""
        if not self.subject_identifier_as_pk:
            self.subject_identifier_as_pk = str(uuid4())  # this will never change
            if not self.subject_identifier:
                self.subject_identifier = self.subject_identifier_as_pk

    def get_registered_subject(self):
        return self

    def get_subject_identifier(self):
        return self.subject_identifier

    def include_for_dispatch(self):
        return True

    def is_serialized(self):
        return True

    def dispatch_container_lookup(self):
        return (self.__class__, 'id')

    def is_dispatched(self):
        return False

    def age(self):
        return self.screening_age_in_years
    age.allow_tags = True

    def dashboard(self):
        ret = None
        if self.subject_identifier:
            try:
                url = reverse('subject_dashboard_url', kwargs={
                    'dashboard_type': self.subject_type.lower(),
                    'dashboard_id': self.pk,
                    'dashboard_model': 'registered_subject',
                    'show': 'appointments'})
                ret = """<a href="{url}" />dashboard</a>""".format(url=url)
            except NoReverseMatch:
                pass
        return ret
    dashboard.allow_tags = True

    class Meta:
        abstract = True
        verbose_name = 'Registered Subject'
        ordering = ['subject_identifier']
        unique_together = ('first_name', 'dob', 'initials', 'additional_key')


@receiver(post_save, weak=False, dispatch_uid="update_registered_subject_from_consent_on_post_save")
def update_registered_subject_from_consent_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates RegisteredSubject from the consent.

    Consent must have an AuditTrail manager (history), a FK to registered_subject
    and an 'identity' field."""
    if not raw and not kwargs.get('update_fields'):
        try:
            instance.history  # raise on models without an AuditTrail, e.g audit model classes
            with transaction.atomic():
                identity = instance.identity  # only a consent model has this field
                registered_subject = instance.registered_subject
                registered_subject.identity = identity
                registered_subject.last_name = instance.last_name
                registered_subject.first_name = instance.first_name
                registered_subject.identity_type = instance.identity_type
                registered_subject.subject_identifier = instance.subject_identifier
                registered_subject.registration_identifier = instance.pk
                registered_subject.dob = instance.dob
                registered_subject.is_dob_estimated = instance.is_dob_estimated
                registered_subject.gender = instance.gender
                registered_subject.initials = instance.initials
                registered_subject.study_site = instance.study_site
                registered_subject.save(using=using)
        except AttributeError as e:
            if '\'NoneType\' object has no attribute \'pk\'' in str(e):
                pass
            elif ('registered_subject' not in str(e) and
                  'identity' not in str(e) and
                  'history' not in str(e) and 'last_name' not in str(e)):
                raise AttributeError(str(e))
