from django.db import models
from django.utils.html import format_html
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_constants.choices import YES_NO
from edc_model.validators import cell_number, telephone_number


class SubjectContactFieldsMixin(models.Model):
    may_call = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=format_html(
            "Has the participant given permission <b>{text}</b> "
            "by study staff for follow-up purposes during the study?",
            text="to contacted by telephone or cell",
        ),
    )

    may_visit_home = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=format_html(
            "Has the participant given permission for study "
            "staff <b>{text}</b> for follow-up purposes?",
            text="to make home visits",
        ),
    )

    may_sms = models.CharField(
        max_length=25,
        choices=YES_NO,
        default="",
        blank=False,
        verbose_name=format_html(
            "Has the participant given permission <b>{text}</b> "
            "by study staff for follow-up purposes during the study?",
            text="to be contacted by SMS",
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
