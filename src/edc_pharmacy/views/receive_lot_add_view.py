"""AJAX endpoint for adding a Lot from the receive-item page modal.

Product and assignment are inferred from the ``order_item`` URL kwarg, so the
client only sends the lot-specific fields.

POST → JSON ``{"pk": "...", "lot_no": "...", "label": "..."}`` on success,
       or ``{"errors": {...}}`` with HTTP 400 on validation failure.
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View

from ..forms.stock import LotAddForm
from ..models import OrderItem


@method_decorator(login_required, name="dispatch")
class ReceiveLotAddView(View):
    def post(self, request, *args, **kwargs):  # noqa: ARG002
        order_item = get_object_or_404(OrderItem, pk=kwargs["order_item"])
        form = LotAddForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.product = order_item.product
            obj.assignment = order_item.product.assignment
            obj.user_created = request.user.username
            obj.user_modified = request.user.username
            obj.save()
            return JsonResponse(
                {
                    "pk": str(obj.pk),
                    "lot_no": obj.lot_no,
                    "label": str(obj),
                }
            )
        return JsonResponse({"errors": form.errors}, status=400)
