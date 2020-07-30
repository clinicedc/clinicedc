from django.core.validators import RegexValidator

from ..utils import ym_pattern

"""
expect 1h20m, 11h5m, etc
"""

hm_validator = RegexValidator(
    r"^([0-9]{1,3}h([0-5]?[0-9]m)?)$",
    message="Invalid format. Expected something like 1h20m, 11h5m, etc",
)

ym_validator = RegexValidator(
    ym_pattern,
    message="Invalid format. Expected something like 4y, 3y5m, 1y0m, 6m, etc. No spaces allowed.",
)

hm_validator2 = RegexValidator(
    r"^([0-9]{1,3}:[0-5][0-9])$", message="Enter a valid time in hour:minutes format"
)
