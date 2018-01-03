from django.db import models
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField
from edc_base.model_validators import TelephoneNumber
from edc_constants.choices import YES_NO
from django.utils.safestring import mark_safe


class SubjectWorkFieldsMixin(models.Model):

    may_call_work = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=mark_safe(
            'Has the participant given permission to contacted <b>at work</b> by telephone '
            'or cell by study staff for follow-up purposes during the study?'))

    subject_work_place = EncryptedTextField(
        verbose_name='Name and location of work place',
        max_length=250,
        validators=[TelephoneNumber, ],
        blank=True,
        null=True)

    subject_work_phone = EncryptedCharField(
        verbose_name='Work contact number',
        blank=True,
        null=True)

    class Meta:
        abstract = True
