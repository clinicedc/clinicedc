from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_email_contacts(key) -> str | None:
    email_contacts = getattr(settings, "EMAIL_CONTACTS", {})
    if not get_email_enabled():
        email_contact = None
        # raise ImproperlyConfigured("Email not enabled. See settings.EMAIL_ENABLED.")
    else:
        if key not in email_contacts:
            raise ImproperlyConfigured(
                f"Key not found. See settings.EMAIL_CONTACTS. Got key=`{key}`."
            )
        email_contact = email_contacts.get(key)
    return email_contact


def get_email_enabled() -> bool:
    return getattr(settings, "EMAIL_ENABLED", False)
