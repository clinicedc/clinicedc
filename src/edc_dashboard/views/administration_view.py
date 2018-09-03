from django.conf import settings
from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AdministrationViewMixin
from edc_navbar import NavbarViewMixin


class AdministrationView(EdcBaseViewMixin, NavbarViewMixin,
                         AdministrationViewMixin, TemplateView):

    navbar_selected_item = 'administration'
    navbar_name = settings.APP_NAME
