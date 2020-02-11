from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style

from .constants import DEFAULT
from .site_randomizers import site_randomizers

style = color_style()
