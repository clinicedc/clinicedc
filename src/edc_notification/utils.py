from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_email_contacts(key) -> dict:
    email_contacts = getattr(settings, "EMAIL_CONTACTS", {})
    if get_email_enabled() and key not in email_contacts:
        raise ImproperlyConfigured(
            f"Key not found. See settings.EMAIL_CONTACTS. Got key=`{key}`."
        )
    return email_contacts.get(key)


def get_email_enabled() -> bool:
    return getattr(settings, "EMAIL_ENABLED", False)
