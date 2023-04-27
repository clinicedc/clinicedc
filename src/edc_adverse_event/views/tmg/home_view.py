from django.contrib.sites.shortcuts import get_current_site
from django.db.models.aggregates import Count
from django.views.generic import TemplateView
from edc_action_item.models.action_item import ActionItem
from edc_constants.constants import CLOSED, NEW, OPEN
from edc_dashboard.utils import get_bootstrap_version
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ...constants import AE_TMG_ACTION


class TmgHomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = f"edc_adverse_event/bootstrap{get_bootstrap_version()}/tmg/tmg_home.html"
    navbar_selected_item = "tmg_home"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # summarize closed reports by site
        summary = (
            ActionItem.objects.filter(action_type__name=AE_TMG_ACTION, status=CLOSED)
            .values("site__name")
            .annotate(count=Count("status"))
            .order_by("site__name")
        )

        # summarize new and open for notice
        qs = (
            ActionItem.objects.filter(action_type__name=AE_TMG_ACTION, status__in=[NEW, OPEN])
            .exclude(site__name=get_current_site(request=self.request).name)
            .values("status", "site__name")
            .annotate(items=Count("status"))
        )
        notices = []
        for item in qs.order_by("status", "site__name"):
            notices.append([item.get("site__name"), item.get("status"), item.get("items")])

        new_count = ActionItem.objects.filter(
            action_type__name=AE_TMG_ACTION,
            site__name=get_current_site(request=self.request).name,
            status=NEW,
        ).count()
        open_count = ActionItem.objects.filter(
            action_type__name=AE_TMG_ACTION,
            site__name=get_current_site(request=self.request).name,
            status=OPEN,
        ).count()
        closed_count = ActionItem.objects.filter(
            action_type__name=AE_TMG_ACTION,
            site__name=get_current_site(request=self.request).name,
            status=CLOSED,
        ).count()
        total_count = ActionItem.objects.filter(
            action_type__name=AE_TMG_ACTION,
            site__name=get_current_site(request=self.request).name,
            status__in=[NEW, OPEN, CLOSED],
        ).count()
        context.update(
            {
                "new_count": new_count,
                "open_count": open_count,
                "closed_count": closed_count,
                "total_count": total_count,
                "summary": summary,
                "notices": notices,
            }
        )
        return context
