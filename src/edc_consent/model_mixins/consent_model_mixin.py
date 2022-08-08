from uuid import uuid4

from django.db import models
from django.db.models import options
from django_crypto_fields.fields import EncryptedTextField
from edc_constants.constants import OPEN
from edc_data_manager.get_data_queries import get_data_queries
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_sites.models import CurrentSiteManager
from edc_utils import age, formatted_age

from ..consent_helper import ConsentHelper
from ..constants import DEFAULT_CONSENT_GROUP
from ..field_mixins import VerificationFieldsMixin
from ..managers import ConsentManager, ObjectConsentManager

if "consent_group" not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("consent_group",)


class ConsentModelMixin(VerificationFieldsMixin, models.Model):
    """Mixin for a Consent model class such as SubjectConsent.

    Declare with edc_identifier's NonUniqueSubjectIdentifierModelMixin
    """

    consent_helper_cls = ConsentHelper

    consent_datetime = models.DateTimeField(
        verbose_name="Consent date and time",
        validators=[datetime_not_before_study_start, datetime_not_future],
    )

    report_datetime = models.DateTimeField(null=True, editable=False)

    version = models.CharField(
        verbose_name="Consent version",
        max_length=10,
        help_text="See 'Consent Type' for consent versions by period.",
        editable=False,
    )

    updates_versions = models.BooleanField(default=False)

    sid = models.CharField(
        verbose_name="SID",
        max_length=15,
        null=True,
        blank=True,
        editable=False,
        help_text="Used for randomization against a prepared rando-list.",
    )

    comment = EncryptedTextField(verbose_name="Comment", max_length=250, blank=True, null=True)

    dm_comment = models.CharField(
        verbose_name="Data Management comment",
        max_length=150,
        null=True,
        editable=False,
        help_text="see also edc.data manager.",
    )

    consent_identifier = models.UUIDField(
        default=uuid4,
        editable=False,
        help_text="A unique identifier for this consent instance",
    )

    objects = ObjectConsentManager()

    consent = ConsentManager()

    on_site = CurrentSiteManager()

    def __str__(self):
        return f"{self.get_subject_identifier()} v{self.version}"

    def natural_key(self):
        return (self.get_subject_identifier_as_pk(),)  # noqa

    def save(self, *args, **kwargs):
        self.report_datetime = self.consent_datetime
        helper = self.get_consent_helper()
        self.version = helper.version
        self.updates_versions = True if helper.updates_versions else False
        super().save(*args, **kwargs)

    def get_consent_helper(self):
        """Returns a consent helper instance"""
        return self.consent_helper_cls(
            model_cls=self.__class__, update_previous=True, **self.__dict__
        )

    def get_subject_identifier(self):
        """Returns the subject_identifier"""
        try:
            return self.subject_identifier  # noqa
        except AttributeError as e:
            if "subject_identifier" in str(e):
                raise NotImplementedError(f"Missing model mixin. Got `{str(e)}`.")
            raise

    def get_subject_identifier_as_pk(self):
        """Returns the subject_identifier_as_pk"""
        try:
            return self.subject_identifier_as_pk  # noqa
        except AttributeError as e:
            if "subject_identifier_as_pk" in str(e):
                raise NotImplementedError(f"Missing model mixin. Got `{str(e)}`.")
            raise

    def get_dob(self):
        """Returns the date of birth"""
        try:
            return self.dob  # noqa
        except AttributeError as e:
            if "dob" in str(e):
                raise NotImplementedError(f"Missing model mixin. Got `{str(e)}`.")
            raise

    @property
    def age_at_consent(self):
        """Returns a relativedelta."""
        try:
            return age(self.get_dob(), self.consent_datetime)
        except AttributeError as e:
            if "dob" in str(e):
                raise NotImplementedError(f"Missing model mixin. Got `{str(e)}`.")
            raise

    @property
    def formatted_age_at_consent(self):
        """Returns a string representation."""
        return formatted_age(self.get_dob(), self.consent_datetime)

    @property
    def open_data_queries(self):
        return get_data_queries(
            subject_identifier=self.subject_identifier,
            model=self._meta.label_lower,
            status=OPEN,
        )

    class Meta:
        abstract = True
        verbose_name = "Subject Consent"
        verbose_name_plural = "Subject Consents"
        consent_group = DEFAULT_CONSENT_GROUP
        get_latest_by = "consent_datetime"
        unique_together = (
            ("first_name", "dob", "initials", "version"),
            ("subject_identifier", "version"),
        )
        ordering = ("created",)

        indexes = [
            models.Index(
                fields=[
                    "subject_identifier",
                    "first_name",
                    "dob",
                    "initials",
                    "version",
                ]
            )
        ]
