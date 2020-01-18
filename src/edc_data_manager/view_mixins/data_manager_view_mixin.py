from django.views.generic.base import ContextMixin
from edc_action_item.model_wrappers import ActionItemModelWrapper
from edc_action_item.models import ActionItem
from edc_constants.constants import NEW, OPEN


class DataManagerViewMixin(ContextMixin):

    action_item_model_wrapper_cls = ActionItemModelWrapper

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(open_data_queries=self.open_data_queries)
        return context

    @property
    def open_data_queries(self):
        """Returns a list of wrapped ActionItem instances
        where status is NEW or OPEN.
        """
        qs = ActionItem.on_site.filter(
            subject_identifier=self.kwargs.get("subject_identifier"),
            reference_model="edc_data_manager.dataquery",
            action_type__show_on_dashboard=True,
            status__in=[NEW, OPEN],
        ).order_by("-report_datetime")
        return [self.action_item_model_wrapper_cls(model_obj=obj) for obj in qs]
