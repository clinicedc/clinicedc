from warnings import warn

from django.conf import settings


def get_email_contacts(key) -> dict:
    email_contacts = getattr(settings, "EMAIL_CONTACTS", {})
    if key not in email_contacts:
        warn(f"Key not found in email_contacts. See settings.EMAIL_CONTACTS. Got key=`{key}`.")
    return email_contacts.get(key)


def get_email_enabled() -> bool:
    email_enabled = getattr(settings, "EMAIL_ENABLED", None)
    if email_enabled is None:
        warn("Settings attribute not set. See settings.EMAIL_ENABLED.")
    return email_enabled or False
