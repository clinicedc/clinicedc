from django.conf import settings
from django.apps import apps as django_apps


def get_consent_model_name():
    return settings.SUBJECT_CONSENT_MODEL


def get_consent_model():
    return django_apps.get_model(get_consent_model_name())


def get_reconsent_model_name():
    return getattr(
        settings,
        "SUBJECT_RECONSENT_MODEL",
        f"{get_consent_model_name().split('.')[0]}.subjectreconsent",
    )


def get_reconsent_model():
    return django_apps.get_model(get_reconsent_model_name())
