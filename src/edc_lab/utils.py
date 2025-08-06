from django.apps import apps as django_apps
from django.conf import settings


def get_requisition_model():
    return django_apps.get_model(get_requisition_model_name())


def get_panel_model():
    return django_apps.get_model(get_panel_model_name())


def get_panel_model_name():
    return getattr(settings, "LAB_PANEL_MODEL", "edc_lab.panel")


def get_requisition_model_name():
    return settings.SUBJECT_REQUISITION_MODEL


def get_subject_requisition_model():
    return get_requisition_model_name()
