from django.conf import settings
from django.views.generic import TemplateView

from edc_navbar import NavbarViewMixin

from ..view_mixins import AdministrationViewMixin, EdcViewMixin


class AdministrationView(EdcViewMixin, NavbarViewMixin, AdministrationViewMixin, TemplateView):
    navbar_selected_item = "administration"
    navbar_name = getattr(settings, "APP_NAME", "default")
