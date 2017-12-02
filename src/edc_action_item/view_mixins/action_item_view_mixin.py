from django.apps import apps as django_apps
from django.views.generic.base import ContextMixin
from edc_constants.constants import CLOSED, CANCELLED


class ActionItemViewMixin(ContextMixin):

    action_item_model = 'edc_action_item.actionitem'
    action_item_model_wrapper_cls = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            open_action_items=self.open_action_items)
        return context

    @property
    def open_action_items(self):
        model_cls = django_apps.get_model(self.action_item_model)
        qs = model_cls.objects.filter(
            subject_identifier=self.kwargs.get('subject_identifier'),
            action_type__show_on_dashboard=True).exclude(
                status__in=[CLOSED, CANCELLED]).order_by('-report_datetime')
        return [self.action_item_model_wrapper_cls(model_obj=obj) for obj in qs]
