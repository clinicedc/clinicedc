from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from ...models import BoxItem
from .base_listboard import BaseListboardView, app_config


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


class AliquotListboardView(BaseListboardView):

    navbar_item_selected = 'aliquot'
    model_name = app_config.aliquot_model
    model_wrapper_class = AliquotModelWrapper
    listboard_url_name = app_config.aliquot_listboard_url_name
    listboard_template_name = app_config.aliquot_listboard_template_name
    show_all = True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config.manifest.update_destinations()
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        if self.request.GET.get('f') == 'is_primary':
            return {'is_primary': True}
        elif self.request.GET.get('f') == 'packed':
            return {'aliquot_identifier__in': BoxItem.objects.all().values('identifier')}
        elif self.request.GET.get('f') == 'all':
            return {}
        return {}

    def get_queryset_exclude_options(self, request, *args, **kwargs):
        if self.request.GET.get('e') == 'not_packed':
            return {'aliquot_identifier__in': BoxItem.objects.all().values('identifier')}
        return {}
