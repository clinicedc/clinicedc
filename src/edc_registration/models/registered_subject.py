from django.conf import settings
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

# from edc_audit.audit_trail import AuditTrail
from edc_base.model.fields import IdentityTypeField
from edc_constants.choices import YES_NO, ALIVE_DEAD_UNKNOWN
from edc_subject.models import BaseSubject

from django_crypto_fields.fields import IdentityField


class RegisteredSubject(BaseSubject):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        blank=True,
        db_index=True,
        unique=True,
    )

    subject_consent_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    registration_identifier = models.CharField(
        max_length=36,
        null=True,
        blank=True,
    )

    sid = models.CharField(
        verbose_name="SID",
        max_length=15,
        null=True,
        blank=True,
    )

    study_site = models.CharField(
        verbose_name='Site',
        max_length=25,
        help_text="",
        null=True,
        blank=True,
    )

    relative_identifier = models.CharField(
        verbose_name="Identifier of immediate relation",
        max_length=25,
        null=True,
        blank=True,
        help_text="For example, mother's identifier, if available / appropriate"
    )

    identity = IdentityField(
        null=True,
        blank=True,
    )

    identity_type = IdentityTypeField()

    may_store_samples = models.CharField(
        verbose_name=_("Sample storage"),
        max_length=3,
        choices=YES_NO,
        default='?',
        help_text=_("Does the subject agree to have samples stored after the study has ended")
    )

    survival_status = models.CharField(
        verbose_name='Survival status',
        max_length=15,
        choices=ALIVE_DEAD_UNKNOWN,
        null=True,
    )

    screening_datetime = models.DateTimeField(
        null=True,
        blank=True
    )

    registration_datetime = models.DateTimeField(
        null=True,
        blank=True
    )

    """ for simplicity, if going straight from screen to rando,
        update both registration date and randomization date """
    randomization_datetime = models.DateTimeField(
        null=True,
        blank=True
    )

    registration_status = models.CharField(
        verbose_name="Registration status",
        max_length=25,
        null=True,
        blank=True,
    )

    comment = models.TextField(
        verbose_name='Comment',
        max_length=250,
        null=True,
        blank=True,
    )

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
                   'is not captured in this model'),
    )

    # history = AuditTrail()

    def save(self, *args, **kwargs):
        self.check_max_subjects()
        if self.identity:
            self.additional_key = None
        super(RegisteredSubject, self).save(*args, **kwargs)

    def __str__(self):
        if self.sid:
            return "{0} {1} ({2} {3})".format(self.mask_unset_subject_identifier(),
                                              self.subject_type,
                                              self.first_name.field_cryptor.mask(self.first_name),
                                              self.sid)
        else:
            return "{0} {1} ({2})".format(self.mask_unset_subject_identifier(),
                                          self.subject_type,
                                          self.first_name.field_cryptor.mask(self.first_name),)

    def check_max_subjects(self, exception_cls=None, settings_attrs=None, count=None):
        """Checks the number of subjects against the settings attribute MAX_SUBJECTS.

        Format is MAX_SUBJECTS = {'maternal': 1000, 'infant': 1500}.

        For testing, you can skip these verifications by using 'test_subject_type' as the subject_type."""
        if not exception_cls:
            exception_cls = ValidationError
        if not settings_attrs:
            settings_attrs = settings
        if not self.id and not self.subject_type == 'test_subject_type':
            self.verify_settings_attr(settings_attrs)
            if 'MAX_SUBJECTS' in dir(settings_attrs):
                # confirm have not reached max number of subjects
                max_subjects = settings_attrs.MAX_SUBJECTS.get(self.get_subject_type(settings_attrs)) or 0
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
            (k, v) for k, v in obj.__dict__.items()
            if k not in ['study_site_id', 'registration_status', 'modified'] and not k.startswith('_')
        ]
        for k, v in may_not_change_these_fields:
            if getattr(self, k) != v:
                return False
        return True

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
        app_label = 'edc_registration'
        verbose_name = 'Registered Subject'
        ordering = ['subject_identifier']
        unique_together = ('first_name', 'dob', 'initials', 'additional_key')
