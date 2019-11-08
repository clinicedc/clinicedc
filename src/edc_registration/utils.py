from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


def get_registered_subject_model_name():
    return "edc_registration.registeredsubject"


def get_registered_subject_model():
    return django_apps.get_model(get_registered_subject_model_name())


def get_registered_subject(subject_identifier):
    registered_subject = None
    try:
        model_cls = get_registered_subject_model()
    except LookupError:
        pass
    else:
        try:
            registered_subject = model_cls.objects.get(
                subject_identifier=subject_identifier
            )
        except ObjectDoesNotExist:
            pass
    return registered_subject
