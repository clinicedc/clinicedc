from edc_action_item.model_wrappers import ActionItemModelWrapper
from edc_action_item.models import ActionItem
from edc_constants.constants import NEW, OPEN, RESOLVED

from edc_data_manager.models import DataQuery


class DataManagerViewMixin:
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
        data_queries = DataQuery.objects.filter(
            subject_identifier=self.kwargs.get("subject_identifier"),
        ).exclude(site_response_status=RESOLVED)
        qs = ActionItem.on_site.filter(
            pk__in=[obj.action_item.id for obj in data_queries], status__in=[NEW, OPEN]
        )
        return [self.action_item_model_wrapper_cls(model_obj=obj) for obj in qs]
