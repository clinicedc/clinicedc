from __future__ import annotations

from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..constants import REVIEW_CATEGORIES
from ..models import Result


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_lab_results/home.html"
    navbar_selected_item = "edc_lab_results"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["review_count"] = Result.objects.filter(
            requisition_match_category__in=REVIEW_CATEGORIES
        ).count()
        return context
