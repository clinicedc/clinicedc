from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_crypto_fields.fields import IdentityField

from edc_base.model.fields import IdentityTypeField


class IdentityFieldsMixin(models.Model):

    identity = IdentityField(
        verbose_name=_("Identity number (OMANG, etc)"),
        unique=True,
        help_text=("Use Omang, Passport number, driver's license number or Omang receipt number")
    )

    identity_type = IdentityTypeField()

    confirm_identity = IdentityField(
        help_text="Retype the identity number from the identity card",
        null=True,
        blank=False
    )

    class Meta:
        abstract = True
