from __future__ import annotations

from django.core.paginator import Paginator
from django.db.models import Count, Min
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..choices import REQUISITION_MATCH_CATEGORY_CHOICES
from ..constants import REVIEW_CATEGORIES
from ..models import Result

PAGE_SIZE = 50

_CATEGORY_LABELS = dict(REQUISITION_MATCH_CATEGORY_CHOICES)


class ReviewWorklistView(EdcViewMixin, NavbarViewMixin, TemplateView):
    """Worklist of orders whose results need human action.

    Groups flagged results by order_no and lets a data manager drill into
    the order detail (the manual-link surface). Only REVIEW_CATEGORIES are
    surfaced; linked and untracked/unmapped results are excluded.
    """

    template_name = "edc_lab_results/review_worklist.html"
    navbar_selected_item = "edc_lab_results"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)

        # Counts per review category (for the filter chips).
        raw_counts = dict(
            Result.objects.filter(requisition_match_category__in=REVIEW_CATEGORIES)
            .values_list("requisition_match_category")
            .annotate(n=Count("id"))
        )
        categories = [
            {
                "value": value,
                "label": _CATEGORY_LABELS.get(value, value),
                "count": raw_counts.get(value, 0),
            }
            for value in REVIEW_CATEGORIES
        ]

        active = self.request.GET.get("category", "").strip()
        if active not in REVIEW_CATEGORIES:
            # Default to the first non-empty category, else the first.
            active = next(
                (c["value"] for c in categories if c["count"]),
                REVIEW_CATEGORIES[0],
            )

        orders_qs = (
            Result.objects.filter(requisition_match_category=active)
            .values(
                "order_no",
                "subject_identifier",
                "screening_identifier",
                "name_id",
                "laboratory",
                "requisition_match_comment",
            )
            .annotate(flagged=Count("id"), order_datetime=Min("order_datetime"))
            .order_by("-order_datetime")
        )

        page_obj = Paginator(orders_qs, PAGE_SIZE).get_page(
            self.request.GET.get("page")
        )

        context.update(
            categories=categories,
            active_category=active,
            active_label=_CATEGORY_LABELS.get(active, active),
            total_flagged=sum(raw_counts.values()),
            page_obj=page_obj,
        )
        return context
