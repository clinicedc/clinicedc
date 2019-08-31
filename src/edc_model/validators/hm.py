from django.core.validators import RegexValidator

hm_validator = RegexValidator(  # noqa
    "^([0-9]{1,3}:[0-5][0-9])$", message="Enter a valid time in hour:minutes format"
)
