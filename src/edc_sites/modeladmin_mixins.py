import warnings

from .admin import SiteModelAdminMixin  # noqa

warnings.warn(
    "This import path is deprecated. Use `edc_sites.admin` instead.",
    DeprecationWarning,
    stacklevel=2,
)
