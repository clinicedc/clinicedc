from django.core.exceptions import ValidationError
from django.db import models
from django_crypto_fields.fields import IdentityField

from edc_base.model_fields import IdentityTypeField


class IdentityFieldsMixin(models.Model):

    identity = IdentityField(
        verbose_name='Identity number (OMANG, etc)',
        help_text=(
            'Use Omang, Passport number, driver\'s license '
            'number or Omang receipt number')
    )

    identity_type = IdentityTypeField()

    confirm_identity = IdentityField(
        help_text='Retype the identity number from the identity card',
        null=True,
        blank=False
    )

    def save(self, *args, **kwargs):
        if self.identity != self.confirm_identity:
            raise ValidationError(
                '\'Identity\' must match \'confirm_identity\'. '
                'Catch this error on the form'
            )
        super(IdentityFieldsMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
