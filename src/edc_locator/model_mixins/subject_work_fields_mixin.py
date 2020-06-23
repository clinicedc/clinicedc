from django.db import models
from django.utils.safestring import mark_safe
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField
from edc_constants.choices import YES_NO
from edc_model.models import telephone_number, cell_number


class SubjectWorkFieldsMixin(models.Model):

    may_call_work = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=mark_safe(
            "Has the participant given permission to contacted <b>at work</b> by telephone "
            "or cell by study staff for follow-up purposes during the study?"
        ),
    )

    subject_work_place = EncryptedTextField(
        verbose_name="Name and location of work place",
        max_length=250,
        blank=True,
        null=True,
    )

    subject_work_phone = EncryptedCharField(
        verbose_name="Work contact telephone",
        validators=[telephone_number],
        blank=True,
        null=True,
    )

    subject_work_cell = EncryptedCharField(
        verbose_name="Work contact cell number",
        validators=[cell_number],
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
