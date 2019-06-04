from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


def get_registered_subject_model():
    return django_apps.get_model("edc_registration.registeredsubject")


def get_registered_subject(subject_identifier):
    registered_subject = None
    try:
        model_cls = django_apps.get_model("edc_registration.registeredsubject")
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
