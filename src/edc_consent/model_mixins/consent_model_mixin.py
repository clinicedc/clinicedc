from uuid import uuid4

from django.db import models
from django.db.models import UniqueConstraint
from django_crypto_fields.fields import EncryptedTextField

from edc_constants.constants import OPEN
from edc_data_manager.get_data_queries import get_data_queries
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_sites.managers import CurrentSiteManager
from edc_utils import age, formatted_age

from ..field_mixins import VerificationFieldsMixin
from ..managers import ConsentObjectsManager
from .consent_version_model_mixin import ConsentVersionModelMixin


class ConsentModelMixin(ConsentVersionModelMixin, VerificationFieldsMixin, models.Model):
    """Mixin for a Consent model class such as SubjectConsent.

    Declare with edc_identifier's NonUniqueSubjectIdentifierModelMixin
    """

    screening_identifier = models.CharField(verbose_name="Screening identifier", max_length=50)

    screening_datetime = models.DateTimeField(
        verbose_name="Screening datetime", null=True, editable=False
    )

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

    objects = ConsentObjectsManager()

    on_site = CurrentSiteManager()

    def __str__(self):
        return f"{self.get_subject_identifier()} v{self.version}"

    def natural_key(self):
        return (self.get_subject_identifier_as_pk(),)

    def save(self, *args, **kwargs):
        if not self.id:
            self.model_name = self._meta.label_lower
        self.report_datetime = self.consent_datetime
        super().save(*args, **kwargs)

    def get_dob(self):
        """Returns the date of birth"""
        return self.dob

    @property
    def age_at_consent(self):
        """Returns a relativedelta."""
        return age(self.get_dob(), self.consent_datetime)

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
                    "screening_identifier",
                    "subject_identifier",
                ],
                name="%(app_label)s_%(class)s_version_uniq",
            ),
        ]
