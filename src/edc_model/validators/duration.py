from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from ..utils import dh_pattern, ymd_pattern

# expect 1h20m, 11h5m, etc
dh_validator = RegexValidator(
    dh_pattern,
    message=_(
        "Invalid format. Expected combinations of days and hours (dh): "
        "Something like 3d2h, 7d, 12h, etc. No spaces allowed."
    ),
)

hm_validator = RegexValidator(
    r"^([0-9]{1,3}h([0-5]?[0-9]m)?)$",
    message=_("Invalid format. Expected something like 1h20m, 11h5m, etc. No spaces allowed."),
)

ymd_validator = RegexValidator(
    ymd_pattern,
    message=_(
        "Invalid format. Expected combinations of years and months (ym): "
        "4y, 3y5m, 1y0m, 6m or days (d): 7d, 0d.  No spaces allowed."
    ),
)

hm_validator2 = RegexValidator(
    r"^([0-9]{1,3}:[0-5][0-9])$",
    message=_("Enter a valid time in hour:minutes format. No spaces allowed."),
)
