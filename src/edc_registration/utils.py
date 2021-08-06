from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def get_registered_subject_model_name():
    return getattr(
        settings,
        "EDC_REGISTRATION_REGISTERED_SUBJECT_MODEL",
        "edc_registration.registeredsubject",
    )


def get_registered_subject_model_cls():
    return django_apps.get_model(get_registered_subject_model_name())


def get_registered_subject(subject_identifier):
    try:
        registered_subject = get_registered_subject_model_cls().get(
            subject_identifier=subject_identifier
        )
    except ObjectDoesNotExist:
        registered_subject = None
    return registered_subject
