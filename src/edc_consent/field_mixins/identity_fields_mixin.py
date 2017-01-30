from django.core.exceptions import ValidationError
from django.db import models
from django_crypto_fields.fields import IdentityField
from django_crypto_fields.mixins import CryptoMixin

from edc_base.model.fields import IdentityTypeField


class IdentityFieldsMixin(CryptoMixin, models.Model):

    identity = IdentityField(
        verbose_name='Identity number')

    identity_type = IdentityTypeField()

    confirm_identity = IdentityField(
        help_text='Retype the identity number',
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
