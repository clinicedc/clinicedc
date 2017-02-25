from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.forms import SearchForm as BaseSearchForm
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView
from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from ...models import BoxItem
from django.urls.base import reverse

app_name = 'edc_lab'
app_config = django_apps.get_app_config(app_name)


class AliquotModelWrapper(ModelWrapper):

    model_name = 'edc_lab.aliquot'

    @property
    def human_aliquot_identifier(self):
        return self._original_object.human_aliquot_identifier

    @property
    def box_item(self):
        try:
            return BoxItem.objects.get(identifier=self.aliquot_identifier)
        except BoxItem.DoesNotExist:
            return None


class AliquotListboardView(AppConfigViewMixin,
                           EdcBaseViewMixin,
                           ListboardView):

    app_config_name = 'edc_lab'
    navbar_item_selected = 'aliquot'
    navbar_name = 'specimens'
    model = django_apps.get_model(*app_config.aliquot_model.split('.'))
    model_wrapper_class = AliquotModelWrapper
    empty_queryset_message = 'No aliquots to display'
    listboard_template_name = app_config.aliquot_listboard_template_name
    listboard_url_name = app_config.aliquot_listboard_url_name

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        return [self.listboard_template_name]

    @property
    def search_form(self):
        self.search_form_class.action_url = reverse(
            self.listboard_url_name)
        return self.search_form_class

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config.manifest.update_destinations()
        context.update(
            manage_listboard_url_name=app_config.manage_box_listboard_url_name,
            manifest_listboard_url_name=app_config.manifest_listboard_url_name,
            empty_queryset_message=self.empty_queryset_message)
        return context
