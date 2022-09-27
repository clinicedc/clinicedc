import warnings

from .form_validator_mixins import FormValidatorMixin  # noqa

warnings.warn(
    "This path is deprecated in favor of form_validator_mixins.",
    DeprecationWarning,
    stacklevel=2,
)
