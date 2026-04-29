"""Print a Purchase Order to PDF.

GET /edc_pharmacy/order/<order>/print/

Side effects:
- On the FIRST print of an order, sets ``Order.printed=True``,
  ``Order.printed_datetime``, and ``Order.printed_by``. Subsequent prints
  regenerate the PDF without modifying these fields, so the audit trail
  records the original send event.
- Refuses to print if the order has zero items: flashes an error and
  redirects back to the per-order page.
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from ..auth_objects import PHARMACIST_ROLE
from ..models import Order
from ..pdf_reports import NumberedCanvas, OrderReport
from .auths_view_mixin import user_has_pharmacist_role


@login_required
def print_order_view(request, order=None):
    if not user_has_pharmacist_role(request.user):
        raise PermissionDenied(
            f"The {PHARMACIST_ROLE} role is required to print a Purchase Order."
        )

    order = get_object_or_404(Order, pk=order)

    if order.item_count == 0:
        messages.error(
            request,
            f"Cannot print order {order.order_identifier}: it has no items.",
        )
        return HttpResponseRedirect(
            reverse("edc_pharmacy:order_url", kwargs={"order": order.pk})
        )

    # First-print stamping: record the user and timestamp once.
    if not order.printed:
        order.printed = True
        order.printed_datetime = timezone.now()
        order.printed_by = request.user.username
        order.save(
            update_fields=["printed", "printed_datetime", "printed_by"]
        )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="purchase_order_{order.order_identifier}.pdf"'
    )
    page = dict(
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1.5 * cm,
        pagesize=A4,
    )
    report = OrderReport(
        order=order,
        request=request,
        footer_row_height=60,
        page=page,
        numbered_canvas=NumberedCanvas,
    )
    report.build(response)
    return response
