from uuid import uuid4

from django.db import models, transaction
from django.db.models import UniqueConstraint
from django_crypto_fields.fields import EncryptedTextField
from edc_constants.constants import OPEN
from edc_data_manager.get_data_queries import get_data_queries
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_sites.managers import CurrentSiteManager
from edc_sites.site import sites as site_sites
from edc_utils import age, formatted_age

from .. import site_consents
from ..exceptions import SiteConsentError
from ..field_mixins import VerificationFieldsMixin
from ..managers import ConsentManager, ObjectConsentManager


class ConsentModelMixin(VerificationFieldsMixin, models.Model):
    """Mixin for a Consent model class such as SubjectConsent.

    Declare with edc_identifier's NonUniqueSubjectIdentifierModelMixin
    """

    model_name = models.CharField(
        verbose_name="model",
        max_length=50,
        help_text=(
            "label_lower of this model class. Will be different if "
            "instance has been added/edited via a proxy model"
        ),
        null=True,
        editable=False,
    )

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
        if not self.id:
            self.model_name = self._meta.label_lower
        self.report_datetime = self.consent_datetime
        consent_definition = self.get_consent_definition()
        self.version = consent_definition.version
        self.updates_versions = True if consent_definition.updates_versions else False
        if self.updates_versions:
            with transaction.atomic():
                consent_definition.get_previous_consent(
                    subject_identifier=self.subject_identifier,
                    version=self.version,
                )
        super().save(*args, **kwargs)

    def get_consent_definition(self):
        """Allow the consent to save as long as there is a
        consent definition for this report_date and site.
        """
        site = self.site
        if not self.id and not site:
            site = site_sites.get_current_site_obj()
        consent_definition = site_consents.get_consent_definition(
            model=self._meta.label_lower,
            report_datetime=self.consent_datetime,
            site=site_sites.get(site.id),
        )
        if consent_definition.model != self._meta.label_lower:
            raise SiteConsentError(
                f"No consent definitions exist for this consent model. Got {self}."
            )
        return consent_definition

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
        constraints = [
            UniqueConstraint(
                fields=["first_name", "dob", "initials", "version"],
                name="%(app_label)s_%(class)s_first_uniq",
            ),
            UniqueConstraint(
                fields=[
                    "subject_identifier",
                    "first_name",
                    "dob",
                    "initials",
                    "version",
                ],
                name="%(app_label)s_%(class)s_subject_uniq",
            ),
            UniqueConstraint(
                fields=[
                    "version",
                    "subject_identifier",
                ],
                name="%(app_label)s_%(class)s_version_uniq",
            ),
        ]
