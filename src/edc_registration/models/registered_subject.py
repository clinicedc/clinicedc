import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.utils.translation import gettext as _
from django_crypto_fields.fields import FirstnameField, LastnameField
from django_crypto_fields.fields import IdentityField, EncryptedCharField
from edc_constants.choices import GENDER
from edc_constants.constants import UUID_PATTERN
from edc_identifier.model_mixins import UniqueSubjectIdentifierModelMixin
from edc_model import models as edc_models
from edc_model_fields.fields import IdentityTypeField, IsDateEstimatedField
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_uuid

from .managers import RegisteredSubjectManager


class RegisteredSubjectError(Exception):
    pass


class RegisteredSubject(
    UniqueSubjectIdentifierModelMixin, SiteModelMixin, edc_models.BaseUuidModel
):
    """A model mixin for the RegisteredSubject model (only).
    """

    # may not be available when instance created (e.g. infants prior to birth
    # report)
    first_name = FirstnameField(null=True)

    # may not be available when instance created (e.g. infants or household
    # subject before consent)
    last_name = LastnameField(verbose_name="Last name", null=True)

    # may not be available when instance created (e.g. infants)
    initials = EncryptedCharField(
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{2,3}$",
                message=(
                    "Ensure initials consist of letters "
                    "only in upper case, no spaces."
                ),
            )
        ],
        null=True,
    )

    dob = models.DateField(
        verbose_name=_("Date of birth"),
        null=True,
        blank=False,
        help_text=_("Format is YYYY-MM-DD"),
    )

    is_dob_estimated = IsDateEstimatedField(
        verbose_name=_("Is date of birth estimated?"), null=True, blank=False
    )

    gender = models.CharField(
        verbose_name="Gender", max_length=1, choices=GENDER, null=True, blank=False
    )

    subject_consent_id = models.CharField(max_length=100, null=True, blank=True)

    registration_identifier = models.CharField(max_length=36, null=True, blank=True)

    sid = models.CharField(verbose_name="SID", max_length=15, null=True, blank=True)

    subject_type = models.CharField(max_length=25, null=True, blank=True)

    relative_identifier = models.CharField(
        verbose_name="Identifier of immediate relation",
        max_length=36,
        null=True,
        blank=True,
        help_text="For example, mother's identifier, if available / appropriate",
    )

    identity = IdentityField(null=True, blank=True)

    identity_or_pk = models.CharField(
        verbose_name="identity or pk",
        max_length=75,
        unique=True,
        default=get_uuid,
        editable=False,
    )

    identity_type = IdentityTypeField(null=True, blank=True)

    screening_identifier = models.CharField(max_length=36, null=True, blank=True)

    screening_datetime = models.DateTimeField(null=True, blank=True)

    screening_age_in_years = models.IntegerField(null=True, blank=True)

    registration_datetime = models.DateTimeField(null=True, blank=True)

    # For simplicity, if going straight from screen to rando,
    # update both registration date and randomization date
    randomization_datetime = models.DateTimeField(null=True, blank=True)

    registration_status = models.CharField(
        verbose_name="Registration status", max_length=25, null=True, blank=True
    )

    consent_datetime = models.DateTimeField(null=True, blank=True)

    comment = models.TextField(
        verbose_name="Comment", max_length=250, null=True, blank=True
    )

    additional_key = models.CharField(
        max_length=36,
        verbose_name="-",
        editable=False,
        default=None,
        null=True,
        help_text=(
            "A uuid (or some other text value) to be added to bypass the "
            "unique constraint of just firstname, initials, and dob."
            "The default constraint proves limiting since the source "
            "model usually has some other attribute in additional to "
            "first_name, initials and dob which is not captured in "
            "this model"
        ),
    )

    dm_comment = models.CharField(
        verbose_name="Data Management comment",
        max_length=150,
        null=True,
        editable=False,
    )

    randomization_list_model = models.CharField(max_length=150, null=True)

    on_site = CurrentSiteManager()

    history = edc_models.HistoricalRecords()

    objects = RegisteredSubjectManager()

    def save(self, *args, **kwargs):
        if self.identity:
            self.additional_key = None
            self.identity_or_pk = self.identity
        self.set_uuid_as_subject_identifier_if_none()
        self.raise_on_duplicate("subject_identifier")
        self.raise_on_duplicate("identity")
        self.raise_on_changed_subject_identifier()
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier_as_pk,)

    def __str__(self):
        return self.masked_subject_identifier

    natural_key.dependencies = ["sites.Site"]

    def update_subject_identifier_on_save(self):
        """Overridden to not set the subject identifier on save.
        """
        if not self.subject_identifier:
            self.subject_identifier = self.subject_identifier_as_pk.hex
        elif re.match(UUID_PATTERN, self.subject_identifier):
            pass
        return self.subject_identifier

    def make_new_identifier(self):
        return self.subject_identifier_as_pk.hex

    @property
    def masked_subject_identifier(self):
        """Returns the subject identifier, if set, otherwise
        the string '<identifier not set>'.
        """
        if not self.subject_identifier_is_set:
            return "<identifier not set>"
        return self.subject_identifier

    @property
    def subject_identifier_is_set(self):
        """Returns True if subject identifier has been set to a
        subject identifier; that is, no longer the default UUID.
        """
        is_set = True
        try:
            obj = self.__class__.objects.get(pk=self.id)
        except ObjectDoesNotExist:
            is_set = False
        else:
            if re.match(UUID_PATTERN, obj.subject_identifier):
                return False
        return is_set

    def raise_on_changed_subject_identifier(self):
        """Raises an exception if there is an attempt to change
        the subject identifier for an existing instance if the subject
        identifier is already set.
        """
        if self.id and self.subject_identifier_is_set:
            with transaction.atomic():
                obj = self.__class__.objects.get(pk=self.id)
                if obj.subject_identifier != self.subject_identifier_as_pk.hex:
                    if self.subject_identifier != obj.subject_identifier:
                        raise RegisteredSubjectError(
                            "Subject identifier cannot be changed for "
                            "existing registered subject. "
                            f"Got {self.subject_identifier} <> {obj.subject_identifier}."
                        )

    def raise_on_duplicate(self, attrname):
        """Checks if the subject identifier (or other attr) is in use,
        for new and existing instances.
        """
        if getattr(self, attrname):
            with transaction.atomic():
                error_msg = (
                    f"Cannot {{action}} registered subject with a duplicate "
                    f"'{attrname}'. Got {getattr(self, attrname)}."
                )
                try:
                    obj = self.__class__.objects.exclude(
                        **{"pk": self.pk} if self.id else {}
                    ).get(**{attrname: getattr(self, attrname)})
                    if not self.id:
                        raise RegisteredSubjectError(error_msg.format(action="insert"))
                    elif self.subject_identifier_is_set and obj.id != self.id:
                        raise RegisteredSubjectError(error_msg.format(action="update"))
                    else:
                        raise RegisteredSubjectError(error_msg.format(action="update"))
                except ObjectDoesNotExist:
                    pass

    def set_uuid_as_subject_identifier_if_none(self):
        """Inserts a random uuid as a dummy identifier for a new
        instance.

        Model uses subject_identifier_as_pk as a natural key for
        serialization/deserialization. Value must not change
        once set.
        """
        if not self.subject_identifier:
            self.subject_identifier = self.subject_identifier_as_pk.hex

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Registered Subject"
        ordering = ["subject_identifier"]
        unique_together = ("first_name", "dob", "initials", "additional_key")
        indexes = [
            models.Index(fields=["first_name", "dob", "initials", "additional_key"]),
            models.Index(
                fields=["identity", "subject_identifier", "screening_identifier"]
            ),
        ]
        permissions = (
            ("display_firstname", "Can display first name"),
            ("display_lastname", "Can display last name"),
            ("display_dob", "Can display DOB"),
            ("display_identity", "Can display identity number"),
            ("display_initials", "Can display initials"),
        )
