from django.db.models.fields import CharField
from django.utils.translation import gettext as _
from edc_constants.choices import DATE_ESTIMATED, DATE_ESTIMATED_NA
from edc_constants.constants import NOT_APPLICABLE


class IsDateEstimatedField(CharField):

    """field to question if date is estimated"""

    description = _("Custom field to question if date is estimated")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("editable", True)
        kwargs.setdefault("max_length", 25)
        kwargs.setdefault("choices", DATE_ESTIMATED)
        kwargs.setdefault(
            "help_text",
            _(
                "If the exact date is not known, please indicate which "
                "part of the date is estimated."
            ),
        )
        CharField.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "CharField"


class IsDateEstimatedFieldNa(CharField):

    """field to question if date is estimated"""

    description = _("Custom field to question if date is estimated")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("editable", True)
        kwargs.setdefault("null", False)
        kwargs.setdefault("blank", False)
        kwargs.setdefault("max_length", 25)
        kwargs.setdefault("choices", DATE_ESTIMATED_NA)
        kwargs.setdefault("default", NOT_APPLICABLE)
        kwargs.setdefault(
            "help_text",
            _(
                "If the exact date is not known, please indicate which "
                "part of the date is estimated."
            ),
        )
        CharField.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "CharField"
