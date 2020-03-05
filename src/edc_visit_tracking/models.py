from django.apps import apps as django_apps
from django.conf import settings


def get_visit_tracking_model():
    return django_apps.get_model(settings.SUBJECT_VISIT_MODEL)
