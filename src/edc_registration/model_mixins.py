import re

from uuid import uuid4

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.validators import RegexValidator
from django_crypto_fields.fields import (
    IdentityField, EncryptedCharField, FirstnameField, LastnameField)
from django_crypto_fields.mask_encrypted import mask_encrypted
from django.db import models, transaction
from django.utils.translation import ugettext as _

from edc_base.model.constants import DEFAULT_BASE_FIELDS
from edc_base.model.fields import IdentityTypeField
from edc_base.model.fields.custom_fields import IsDateEstimatedField
from edc_constants.choices import YES, NO, GENDER

from .exceptions import RegisteredSubjectError
from .managers import RegisteredSubjectManager

edc_protocol_app_config = django_apps.get_app_config('edc_protocol')

YES_NO_UNKNOWN = (
    (YES, 'Yes'),
    (NO, 'No'),
    ('?', 'Unknown'),
)


class RegisteredSubjectModelMixin(models.Model):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        unique=True,
        editable=False)

    subject_identifier_as_pk = models.CharField(
        verbose_name="Subject Identifier as pk",
        max_length=50,
        editable=False,
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
        choices=GENDER,
        null=True,
        blank=False)

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

    identity_type = IdentityTypeField(
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

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if self.identity:
            self.additional_key = None
        self.set_uuid_as_subject_identifier_if_none()
        self.raise_on_duplicate_subject_identifier(using)
        self.raise_on_changed_subject_identifier(using)
        super(RegisteredSubjectModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier_as_pk, )

    def __str__(self):
        return self.subject_identifier

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


class RegistrationMixin(models.Model):

    """A model mixin that creates or updates RegisteredSubject on post_save signal."""

    def allocate_subject_identifier(self):
        pass

    @property
    def registration_model(self):
        return django_apps.get_app_config('edc_registration').model

    def registration_update_or_create(self):
        """Creates or Updates the registration model with attributes from this instance."""
        self.registration_raise_on_not_unique()
        registered_subject, created = self.registration_model.objects.update_or_create(
            **{self.registration_unique_field: getattr(self, self.registration_unique_field)},
            defaults=self.registration_options)
        return registered_subject, created

    @property
    def registration_unique_field(self):
        return 'subject_identifier'

    def registration_raise_on_not_unique(self):
        """Asserts the field specified for update_or_create is unique."""
        unique_fields = []
        for f in self.registration_model._meta.get_fields():
            try:
                if f.unique:
                    unique_fields.append(f.name)
            except AttributeError:
                pass
        if self.registration_unique_field not in unique_fields:
            raise ImproperlyConfigured('Field is not unique. Got {}.{} -- {}'.format(
                self._meta.label_lower, self.registration_unique_field))

    @property
    def registration_options(self):
        """Gathers values for common attributes between the registration model and this instance."""
        registration_options = {}
        rs = self.registration_model()
        for k, v in self.__dict__.items():
            if k not in DEFAULT_BASE_FIELDS + ['_state'] + [self.registration_unique_field]:
                try:
                    getattr(rs, k)
                    registration_options.update({k: v})
                except AttributeError:
                    pass
        return registration_options

    class Meta:
        abstract = True


class RegisteredSubjectMixin(models.Model):

    """A mixin to ensure subject_identifier is on the model and always updated by the registration model."""

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        editable=False)

    def save(self, *args, **kwargs):
        self.subject_identifier = self.registration_instance.subject_identifier
        super(RegisteredSubjectMixin, self).save(*args, **kwargs)

    @property
    def registration_instance(self):
        registration_instance = None
        try:
            model = django_apps.get_app_config('edc_registration').model
            registration_instance = model.objects.get(subject_identifier=self.subject_identifier)
        except model.DoesNotExist as e:
            raise model.DoesNotExist('{} subject_identifier=\'{}\''.format(str(e), self.subject_identifier))
        return registration_instance

    class Meta:
        abstract = True
