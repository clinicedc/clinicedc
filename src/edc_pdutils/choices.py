from django.conf import settings

from .constants import CSV


APP_LABELS = (
    ((x, x) for x in [app_label.split('.')[0]
                      for app_label in settings.INSTALLED_APPS]),
)
