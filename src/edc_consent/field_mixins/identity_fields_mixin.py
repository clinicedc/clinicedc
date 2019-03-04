from django.db import models
from django_crypto_fields.fields import IdentityField
from django_crypto_fields.models import CryptoMixin

from ..choices import IDENTITY_TYPE


class IdentityFieldsMixinError(Exception):
    pass


class IdentityFieldsMixin(CryptoMixin, models.Model):

    """
    Note: specify identifier_type CHOICES on the form.
    For example:

        from edc_constants.choices import IDENTITY_TYPE

        identity_type = forms.CharField(
            label='What type of identity number is this?',
            widget=forms.RadioSelect(choices=list(IDENTITY_TYPE)))
    """

    identity = IdentityField(verbose_name="Identity number")

    identity_type = models.CharField(
        verbose_name="What type of identity number is this?",
        max_length=25,
        choices=IDENTITY_TYPE,
    )

    confirm_identity = IdentityField(
        help_text="Retype the identity number", null=True, blank=False
    )

    def save(self, *args, **kwargs):
        if self.identity != self.confirm_identity:
            raise IdentityFieldsMixinError(
                "'Identity' must match 'confirm_identity'. "
                "Catch this error on the form"
            )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
