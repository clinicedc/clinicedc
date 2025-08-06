import warnings

from .utils import get_ae_model, get_ae_model_name  # noqa

warnings.warn(
    "This path is deprecated in favor of edc_adverse_event.utils.",
    DeprecationWarning,
    stacklevel=2,
)
