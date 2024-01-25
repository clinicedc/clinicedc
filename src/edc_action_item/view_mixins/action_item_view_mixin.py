from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from edc_constants.constants import NEW, OPEN
from edc_sites.site import sites

from ..models import ActionItem


class ActionItemViewMixin:
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(open_action_items=self.open_action_items)
        return super().get_context_data(**kwargs)

    @property
    def open_action_items(self) -> QuerySet[ActionItem]:
        """Returns a list of wrapped ActionItem instances
        where status is NEW or OPEN.
        """
        return ActionItem.objects.filter(
            subject_identifier=self.kwargs.get("subject_identifier"),
            action_type__show_on_dashboard=True,
            status__in=[NEW, OPEN],
            site_id__in=sites.get_site_ids_for_user(request=self.request),
        ).order_by("-report_datetime")
