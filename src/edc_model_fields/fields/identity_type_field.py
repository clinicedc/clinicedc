from django.utils.translation import gettext as _
from django.db.models import CharField
from edc_constants.choices import IDENTITY_TYPE


class IdentityTypeField(CharField):

    """
        have IdentityTypeField immediately follow an identity field:

        For example,

        ...

        identity = models.CharField(
            verbose_name=_("Identity number (OMANG, etc)"),
            max_length=25,
            unique=True,
            help_text=_(
                "Use Omang, Passport number, driver's license "
                "number or Omang receipt number")
            )

        identity_type = IdentityTypeField()

        ...

        Use the value of identity_type to check the cleaned
        value of identity at the form level.
    """

    description = _("Custom field for Identity Type")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("verbose_name", _("What type of identity number is this?"))
        kwargs.setdefault("editable", True)
        kwargs.setdefault("max_length", 15)
        kwargs.setdefault("choices", IDENTITY_TYPE)
        CharField.__init__(self, *args, **kwargs)
