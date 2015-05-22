from django.utils import timezone

from django.db import models
from django.utils.translation import ugettext as _
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_base.model.validators import CellNumber, TelephoneNumber
from edc_base.model.validators import datetime_not_before_study_start, datetime_not_future
from edc_consent.models import BaseConsentedUuidModel
from edc_constants.choices import YES_NO, YES_NO_DOESNT_WORK
from edc_registration.models import RegisteredSubject

from ..managers import BaseLocatorManager


class BaseLocator(BaseConsentedUuidModel):

    registered_subject = models.OneToOneField(RegisteredSubject, null=True)

    report_datetime = models.DateTimeField(
        verbose_name="Today's date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        default=timezone.now(),
    )

    date_signed = models.DateField(
        verbose_name="Date Locator Form signed ",
        default=timezone.now(),
        help_text="",
    )

    mail_address = EncryptedTextField(
        max_length=500,
        verbose_name=_("Mailing address "),
        help_text="",
        null=True,
        blank=True
    )

    home_visit_permission = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to make home visits for follow-up purposes during the study?"),
    )

    physical_address = EncryptedTextField(
        max_length=500,
        verbose_name=_("Physical address with detailed description"),
        blank=True,
        null=True,
        help_text="",
    )

    may_follow_up = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to call her for follow-up purposes during the study?"),
    )

    may_sms_follow_up = models.CharField(
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to SMS her for follow-up purposes during the study?"),
    )

    subject_cell = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number"),
        validators=[CellNumber, ],
        blank=True,
        null=True,
        help_text="",
    )

    subject_cell_alt = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number (alternate)"),
        validators=[CellNumber, ],
        help_text="",
        blank=True,
        null=True,
    )

    subject_phone = EncryptedCharField(
        max_length=8,
        verbose_name=_("Telephone"),
        validators=[TelephoneNumber, ],
        help_text="",
        blank=True,
        null=True,
    )

    subject_phone_alt = EncryptedCharField(
        max_length=8,
        verbose_name=_("Telephone (alternate)"),
        help_text="",
        validators=[TelephoneNumber, ],
        blank=True,
        null=True,
    )

    may_call_work = models.CharField(
        max_length=25,
        choices=YES_NO_DOESNT_WORK,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to contact her at work for follow up purposes during the study?"),
    )

    subject_work_place = EncryptedTextField(
        max_length=500,
        verbose_name=_("Name and location of work place"),
        help_text="",
        blank=True,
        null=True,
    )

    subject_work_phone = EncryptedCharField(
        max_length=8,
        verbose_name=_("Work telephone number "),
        help_text="",
        validators=[TelephoneNumber, ],
        blank=True,
        null=True,
    )

    may_contact_someone = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to contact anyone else for follow-up purposes during the study?"),
        help_text="For example a partner, spouse, family member, neighbour ...",
    )

    contact_name = EncryptedCharField(
        max_length=35,
        verbose_name=_("Full names of the contact person"),
        blank=True,
        null=True,
        help_text="",
    )

    contact_rel = EncryptedCharField(
        max_length=35,
        verbose_name=_("Relationship to participant"),
        blank=True,
        null=True,
        help_text="",
    )

    contact_physical_address = EncryptedTextField(
        max_length=500,
        verbose_name=_("Full physical address "),
        blank=True,
        null=True,
        help_text="",
    )

    contact_cell = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number"),
        validators=[CellNumber, ],
        help_text="",
        blank=True,
        null=True,
    )

    contact_phone = EncryptedCharField(
        max_length=8,
        verbose_name=_("Telephone number"),
        validators=[TelephoneNumber, ],
        help_text="",
        blank=True,
        null=True,
    )

    objects = BaseLocatorManager()

    def natural_key(self):
        return (self.report_datetime,) + self.registered_subject.natural_key()

    class Meta:
        abstract = True
