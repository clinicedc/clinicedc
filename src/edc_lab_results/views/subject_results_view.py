from __future__ import annotations

from django.db.models import Min, Q
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..models import Result


class SubjectResultsView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_lab_results/subject_results.html"
    navbar_selected_item = "edc_lab_results"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        identifier = self.request.GET.get("identifier", "").strip()
        orders: list[dict] = []

        if identifier:
            qs = Result.objects.filter(
                Q(subject_identifier=identifier)
                | Q(screening_identifier=identifier)
                | Q(order_no=identifier)
            )
            orders = list(
                qs.values("order_no", "visit_code", "visit_code_sequence")
                .annotate(
                    earliest_collected=Min("specimen_collected_datetime"),
                    order_datetime=Min("order_datetime"),
                )
                .order_by("-order_datetime")
            )

        context.update(
            identifier=identifier,
            orders=orders,
        )
        return context
