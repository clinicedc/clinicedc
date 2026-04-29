"""Site stock report.

Shows stock currently held at site locations (non-Central), grouped by
location → container type → container.  Excludes dispensed, returned
(location moved back to Central), zero-unit, and invalid items.

For PHARMACIST_ROLE users an extra Assignment column is shown.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..auth_objects import PHARMACIST_ROLE
from ..constants import ZERO_ITEM
from ..models import Stock
from ..models.medication import Assignment
from .auths_view_mixin import AuthsViewMixin


@method_decorator(login_required, name="dispatch")
class SiteStockReportView(
    AuthsViewMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    """Unit-qty in/out/balance for stock currently held at site locations."""

    template_name = "edc_pharmacy/stock/site_stock_report.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        roles = [obj.name for obj in self.request.user.userprofile.roles.all()]
        show_assignment = PHARMACIST_ROLE in roles

        assignment_map: dict = {}
        if show_assignment:
            assignment_map = {str(a.pk): str(a) for a in Assignment.objects.all()}

        values_fields = [
            "location__display_name",
            "location__name",
            "location_id",
            "container__container_type__display_name",
            "container__container_type__name",
            "container__display_name",
            "container__name",
            "container_id",
        ]
        if show_assignment:
            values_fields.append("lot__assignment_id")

        order_fields = [
            "location__display_name",
            "container__container_type__display_name",
            "container__display_name",
        ]
        if show_assignment:
            order_fields.append("lot__assignment_id")

        qs = (
            Stock.objects.filter(
                invalid_state=False,
                dispensed=False,
                location__site__isnull=False,
            )
            .exclude(status=ZERO_ITEM)
            .values(*values_fields)
            .annotate(
                total_unit_qty_in=Sum("unit_qty_in"),
                total_unit_qty_out=Sum("unit_qty_out"),
                stock_count=Count("id"),
            )
            .order_by(*order_fields)
        )

        # Group by location for template rendering
        groups: dict[str, dict] = defaultdict(lambda: {
            "rows": [],
            "subtotal_in": Decimal(0),
            "subtotal_out": Decimal(0),
        })

        grand_in = Decimal(0)
        grand_out = Decimal(0)

        for row in qs:
            location_label = row["location__display_name"] or row["location__name"] or "—"
            ct_label = (
                row["container__container_type__display_name"]
                or row["container__container_type__name"]
                or "—"
            )
            container_label = row["container__display_name"] or row["container__name"] or "—"
            unit_in = row["total_unit_qty_in"] or Decimal(0)
            unit_out = row["total_unit_qty_out"] or Decimal(0)
            balance = unit_in - unit_out

            assignment_label = ""
            if show_assignment:
                assignment_id = str(row.get("lot__assignment_id") or "")
                assignment_label = assignment_map.get(assignment_id, "—")

            groups[location_label]["rows"].append({
                "container_type": ct_label,
                "container": container_label,
                "assignment": assignment_label,
                "stock_count": int(row["stock_count"] or 0),
                "unit_qty_in": unit_in,
                "unit_qty_out": unit_out,
                "balance": balance,
            })
            groups[location_label]["subtotal_in"] += unit_in
            groups[location_label]["subtotal_out"] += unit_out
            grand_in += unit_in
            grand_out += unit_out

        group_list = [
            {
                "location": loc_label,
                "rows": g["rows"],
                "subtotal_in": g["subtotal_in"],
                "subtotal_out": g["subtotal_out"],
                "subtotal_balance": g["subtotal_in"] - g["subtotal_out"],
            }
            for loc_label, g in sorted(groups.items())
        ]

        totals = {
            "unit_qty_in": grand_in,
            "unit_qty_out": grand_out,
            "balance": grand_in - grand_out,
        }

        return super().get_context_data(
            groups=group_list,
            totals=totals,
            show_assignment=show_assignment,
            **kwargs,
        )
