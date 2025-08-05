from django.core.validators import RegexValidator

bp_validator = RegexValidator(  # noqa
    r"^\d{1,3}\/\d{1,3}$", message="Enter a valid BP in SYS/DIA format"
)
