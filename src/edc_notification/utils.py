import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_email_contact(key: str) -> str | None:
    """Returns an email address for key or None."""
    if not get_email_enabled():
        email_contact = None
        # raise ImproperlyConfigured("Email not enabled. See settings.EDC_MAIL_ENABLED.")
    else:
        email_contacts = get_all_email_contacts()
        if key not in email_contacts:
            raise ImproperlyConfigured(
                f"Key not found. See settings.EDC_MAIL_CONTACTS. Got key=`{key}`."
            )
        email_contact = email_contacts.get(key)
    return email_contact


def get_email_contacts(key: str):
    warnings.warn(
        "Function get_email_contacts() will be removed in a future release. "
        "Use get_email_contact(key) or get_all_email_contacts() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_email_contact(key)


def get_all_email_contacts() -> dict:
    if hasattr(settings, "EMAIL_CONTACTS"):
        warnings.warn(
            "Settings attribute `EMAIL_CONTACTS` has been renamed to "
            "`EDC_MAIL_CONTACTS`. Update settings. Support for `EMAIL_CONTACTS` "
            "will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not hasattr(settings, "EDC_MAIL_CONTACTS"):
            return getattr(settings, "EMAIL_CONTACTS", {})
    return getattr(settings, "EDC_MAIL_CONTACTS", {})


def get_email_enabled() -> bool:
    if hasattr(settings, "EMAIL_ENABLED"):
        warnings.warn(
            "Settings attribute `EMAIL_ENABLED` has been renamed to "
            "`EDC_MAIL_ENABLED`. Update settings. Support for `EMAIL_ENABLED` "
            "will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not hasattr(settings, "EDC_MAIL_ENABLED"):
            return settings.EMAIL_ENABLED
    return getattr(settings, "EDC_MAIL_ENABLED", False)


def get_default_email_to(name: str) -> tuple[str, ...]:
    default_domain = getattr(settings, "EDC_MAIL_DEFAULT_DOMAIN", "mg.clinicedc.org")
    return (f"{name}.{settings.APP_NAME}@{default_domain}",)
