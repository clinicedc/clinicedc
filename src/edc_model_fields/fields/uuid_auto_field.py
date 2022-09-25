import warnings

from django_audit_fields.fields import UUIDAutoField  # noqa

warnings.warn(
    (
        "The edc_model_fields.UUIDAutoField path is deprecated in favor of "
        "`django_audit_fields.fields.UUIDAutoField`"
    ),
    DeprecationWarning,
    stacklevel=2,
)
