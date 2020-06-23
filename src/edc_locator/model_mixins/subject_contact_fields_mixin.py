from django.db import models
from django.utils.safestring import mark_safe
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField
from edc_model.models import cell_number, telephone_number
from edc_constants.choices import YES_NO


class SubjectContactFieldsMixin(models.Model):

    may_call = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=mark_safe(
            "Has the participant given permission <b>to contacted by telephone "
            "or cell</b> by study staff for follow-up purposes during the study?"
        ),
    )

    may_visit_home = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=mark_safe(
            "Has the participant given permission for study "
            "staff <b>to make home visits</b> for follow-up purposes?"
        ),
    )

    may_sms = models.CharField(
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
        verbose_name=mark_safe(
            "Has the participant given permission <b>to be contacted by SMS</b> "
            "by study staff for follow-up purposes during the study?"
        ),
    )

    mail_address = EncryptedTextField(
        verbose_name="Mailing address ", max_length=500, null=True, blank=True
    )

    physical_address = EncryptedTextField(
        verbose_name="Physical address with detailed description",
        max_length=500,
        blank=True,
        null=True,
        help_text="",
    )

    subject_cell = EncryptedCharField(
        verbose_name="Cell number",
        validators=[cell_number],
        blank=True,
        null=True,
        help_text="",
    )

    subject_cell_alt = EncryptedCharField(
        verbose_name="Cell number (alternate)",
        validators=[cell_number],
        blank=True,
        null=True,
    )

    subject_phone = EncryptedCharField(
        verbose_name="Telephone", validators=[telephone_number], blank=True, null=True
    )

    subject_phone_alt = EncryptedCharField(
        verbose_name="Telephone (alternate)",
        validators=[telephone_number],
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
