from django.db import models
from django.utils.translation import ugettext_lazy as _

from edc.base.model.fields import IdentityTypeField
from edc.base.model.fields.local.bw import EncryptedOmangField


class IdentityFieldsMixin(models.Model):
    """Identity fields for Botswana"""

    identity = EncryptedOmangField(
        verbose_name=_("Identity number (OMANG, etc)"),
        unique=True,
        help_text=("Use Omang, Passport number, driver's license number or Omang receipt number")
        )

    identity_type = IdentityTypeField()

    confirm_identity = EncryptedOmangField(
        help_text="Retype the identity number from the identity card",
        null=True,
        blank=False)

    class Meta:
        abstract = True
