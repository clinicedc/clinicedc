from django.views.generic.base import ContextMixin
from edc_constants.constants import NEW, OPEN

from ..model_wrappers import ActionItemModelWrapper
from ..models import ActionItem


class ActionItemViewMixin(ContextMixin):

    action_item_model_wrapper_cls = ActionItemModelWrapper

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(open_action_items=self.open_action_items)
        return context

    @property
    def open_action_items(self):
        """Returns a list of wrapped ActionItem instances
        where status is NEW or OPEN.
        """
        qs = ActionItem.on_site.filter(
            subject_identifier=self.kwargs.get("subject_identifier"),
            action_type__show_on_dashboard=True,
            status__in=[NEW, OPEN],
        ).order_by("-report_datetime")
        return [self.action_item_model_wrapper_cls(model_obj=obj) for obj in qs]
