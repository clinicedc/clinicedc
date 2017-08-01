from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

from edc_model_wrapper import ModelWrapper
from edc_lab.constants import SHIPPED
from edc_lab.reports import ManifestReport
from edc_lab.models import Manifest

from ..listboard_filters import ManifestListboardViewFilters
from .base_listboard import BaseListboardView

app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ManifestModelWrapper(ModelWrapper):

    model = edc_lab_app_config.manifest_model
    next_url_name = app_config.manifest_listboard_url_name


class ManifestListboardView(BaseListboardView):

    navbar_item_selected = 'manifest'

    form_action_url_name = f'edc_lab_dashboard:manifest_url'
    listboard_url_name = app_config.manifest_listboard_url_name
    listboard_template_name = app_config.manifest_listboard_template_name
    model = edc_lab_app_config.manifest_model
    model_wrapper_class = ManifestModelWrapper
    listboard_view_filters = ManifestListboardViewFilters()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            new_manifest=ManifestModelWrapper(Manifest()),
            print_manifest_url_name=f'edc_lab_dashboard:print_manifest_url',
            SHIPPED=SHIPPED,
        )
        return context

    def get(self, request, *args, **kwargs):
        if request.GET.get('pdf'):
            response = self.print_manifest()
            return response
        return super().get(request, *args, **kwargs)

    @property
    def manifest(self):
        return self.manifest_model.objects.get(
            manifest_identifier=self.request.GET.get('pdf'))

    def print_manifest(self):
        user = User.objects.get(username=self.request.user)
        manifest_report = ManifestReport(
            manifest=self.manifest, user=user)
        return manifest_report.render()
