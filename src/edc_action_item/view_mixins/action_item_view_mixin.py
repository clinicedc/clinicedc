from django.views.generic.base import ContextMixin
from edc_constants.constants import CLOSED, CANCELLED

from ..model_wrappers import ActionItemModelWrapper
from ..models import ActionItem
from ..site_action_items import site_action_items


class ActionItemViewMixin(ContextMixin):

    action_item_model_wrapper_cls = ActionItemModelWrapper

    def __init__(self, **kwargs):
        site_action_items.populate_action_types()
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            open_action_items=self.open_action_items)
        return context

    @property
    def open_action_items(self):
        """Returns a list of wrapped ActionItem instances
        where status is not OPEN.
        """
        qs = ActionItem.objects.filter(
            subject_identifier=self.kwargs.get('subject_identifier'),
            action_type__show_on_dashboard=True).exclude(
                status__in=[CLOSED, CANCELLED]).order_by('-report_datetime')
        return [self.action_item_model_wrapper_cls(model_obj=obj) for obj in qs]
