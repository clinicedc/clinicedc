from django.apps import apps as django_apps
from django.conf import settings


def get_egfr_drop_notification_model():
    return getattr(settings, "EDC_EGFR_DROP_NOTIFICATION_MODEL")


def get_egfr_drop_notification_model_cls():
    return django_apps.get_model(get_egfr_drop_notification_model())
