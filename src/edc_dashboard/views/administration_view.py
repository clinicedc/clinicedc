# from django.conf import settings
from django.views.generic import TemplateView
from edc_dashboard.view_mixins import AdministrationViewMixin, EdcViewMixin
from edc_navbar import NavbarViewMixin


class AdministrationView(
    EdcViewMixin, NavbarViewMixin, AdministrationViewMixin, TemplateView
):

    navbar_selected_item = "administration"
    navbar_name = "default"  # settings.APP_NAME
