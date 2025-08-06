import warnings

from .test_case_mixins import AppointmentTestCaseMixin  # noqa

warnings.warn(
    "This path/func name is deprecated in favor of test_case_mixins.AppointmentTestCaseMixin.",
    DeprecationWarning,
    stacklevel=2,
)
