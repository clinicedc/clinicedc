from typing import Any

from django.db.models import QuerySet

from edc_action_item.models import ActionItem
from edc_constants.constants import NEW, OPEN, RESOLVED
from edc_data_manager.models import DataQuery
from edc_sites.site import sites


class DataManagerViewMixin:
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(open_data_queries=self.open_data_queries)
        return super().get_context_data(**kwargs)

    @property
    def open_data_queries(self) -> QuerySet:
        """Returns a list of wrapped ActionItem instances
        where status is NEW or OPEN.
        """
        data_queries = DataQuery.objects.filter(
            subject_identifier=self.kwargs.get("subject_identifier"),
        ).exclude(site_response_status=RESOLVED)
        qs = ActionItem.objects.filter(
            pk__in=[obj.action_item.id for obj in data_queries],
            status__in=[NEW, OPEN],
            site_id__in=sites.get_site_ids_for_user(request=self.request),
        )
        return qs
