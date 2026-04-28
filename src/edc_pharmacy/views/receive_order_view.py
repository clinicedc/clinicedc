"""Receive workflow — per-order receive page.

Handles three POST actions on a single page:
  save_receive   — create / update the Receive header
  print_labels   — store stock PKs in session → redirect to print-labels view
  confirm_stock  — store stock codes in session → redirect to confirm-stock view

Adding receive items is handled by ReceiveOrderItemView (/receive/<order>/<order_item>/).
"""

from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..auth_objects import PHARMACIST_ROLE
from ..forms.stock import ReceiveHeaderForm
from ..models import Order, OrderItem, Receive, ReceiveItem, Stock
from .auths_view_mixin import AuthsViewMixin


@method_decorator(login_required, name="dispatch")
class ReceiveOrderView(AuthsViewMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    template_name = "edc_pharmacy/stock/receive_order.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs["order"])

    def get_receive(self, order):
        try:
            return Receive.objects.get(order=order)
        except Receive.DoesNotExist:
            return None

    def _build_rows(self, order, receive):
        """Build per-order-item context rows."""
        rows = []
        for oi in OrderItem.objects.filter(order=order).select_related(
            "product", "container"
        ):
            receive_items = (
                ReceiveItem.objects.filter(order_item=oi)
                .select_related("lot", "container")
                .order_by("receive_item_datetime")
            )
            rows.append(
                {
                    "order_item": oi,
                    "receive_items": receive_items,
                    # NULL means signal hasn't run yet — treat as pending
                    "can_add": receive is not None and (
                        oi.unit_qty_pending is None or oi.unit_qty_pending > 0
                    ),
                }
            )
        return rows

    def get_context_data(
        self,
        order=None,
        receive=None,
        receive_form=None,
        rows=None,
        **kwargs,
    ):
        kwargs.pop("order", None)  # remove URL kwarg UUID to avoid passing it upstream
        context = super().get_context_data(**kwargs)
        roles = context.get("roles", [])
        show_batch = PHARMACIST_ROLE in roles
        if not show_batch:
            messages.warning(
                self.request,
                "Batch numbers are hidden. "
                f"You need the {PHARMACIST_ROLE} role to view batch numbers.",
            )

        order = order if isinstance(order, Order) else self.get_order()
        receive = receive if receive is not None else self.get_receive(order)
        receive_form = receive_form or ReceiveHeaderForm(
            instance=receive,
            initial={"supplier": order.supplier},
        )
        rows = rows or self._build_rows(order, receive)

        stock_qs = Stock.objects.filter(receive_item__receive=receive) if receive else None
        confirmed_count = stock_qs.filter(confirmed=True).count() if stock_qs else 0
        unconfirmed_count = stock_qs.filter(confirmed=False).count() if stock_qs else 0

        # edit_receive=True when: no receive yet (must fill form), or ?edit=1 in URL,
        # or the form was re-rendered after a failed POST.
        edit_receive = (
            receive is None
            or self.request.GET.get("edit") == "1"
            or receive_form.errors
        )

        context.update(
            order=order,
            receive=receive,
            receive_form=receive_form,
            rows=rows,
            confirmed_count=confirmed_count,
            unconfirmed_count=unconfirmed_count,
            show_batch=show_batch,
            edit_receive=edit_receive,
        )
        return context

    def post(self, request, *args, **kwargs):
        order = self.get_order()
        receive = self.get_receive(order)
        action = request.POST.get("action")

        if action == "save_receive":
            return self._handle_save_receive(request, order, receive)
        elif action == "print_labels":
            return self._handle_print_labels(request, order, receive)
        elif action == "confirm_stock":
            return self._handle_confirm_stock(request, order, receive)

        return HttpResponseRedirect(
            reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
        )

    def _handle_save_receive(self, request, order, receive):
        from django.utils import timezone
        form = ReceiveHeaderForm(request.POST, instance=receive)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.order = order
            obj.supplier = order.supplier
            # Carry the planned item count from the order on first creation.
            # To change it, edit the order (which updates Order.item_count via signal).
            if not obj.id:
                obj.item_count = order.item_count
            # User supplies the date; server supplies the time
            receive_date = form.cleaned_data["receive_date"]
            now = timezone.localtime(timezone.now())
            obj.receive_datetime = now.replace(
                year=receive_date.year,
                month=receive_date.month,
                day=receive_date.day,
                microsecond=0,
            )
            if not obj.id:
                obj.user_created = request.user.username
            obj.user_modified = request.user.username
            obj.save()
            messages.success(request, f"Receive record {obj.receive_identifier} saved.")
            return HttpResponseRedirect(
                reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
            )
        # Re-render with errors
        receive = self.get_receive(order)
        rows = self._build_rows(order, receive)
        context = self.get_context_data(
            order=order, receive=receive, receive_form=form, rows=rows
        )
        return self.render_to_response(context)

    def _handle_print_labels(self, request, order, receive):
        if not receive:
            messages.error(request, "No receive record found.")
            return HttpResponseRedirect(
                reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
            )
        stock_pks = list(
            Stock.objects.filter(receive_item__receive=receive).values_list("pk", flat=True)
        )
        if not stock_pks:
            messages.warning(request, "No stock items found for this receive record.")
            return HttpResponseRedirect(
                reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
            )
        session_uuid = str(uuid4())
        request.session[session_uuid] = [str(pk) for pk in stock_pks]
        return HttpResponseRedirect(
            reverse(
                "edc_pharmacy:print_labels_url",
                kwargs={"session_uuid": session_uuid, "model": "stock"},
            )
        )

    def _handle_confirm_stock(self, request, order, receive):
        if not receive:
            messages.error(request, "No receive record found.")
            return HttpResponseRedirect(
                reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
            )
        stock_qs = Stock.objects.filter(
            receive_item__receive=receive, confirmed=False
        )
        stock_codes = list(stock_qs.values_list("code", flat=True))
        if not stock_codes:
            messages.warning(request, "All stock items are already confirmed.")
            return HttpResponseRedirect(
                reverse("edc_pharmacy:receive_order_url", kwargs={"order": order.pk})
            )
        session_uuid = str(uuid4())
        request.session[session_uuid] = {
            "stock_codes": stock_codes,
            "source_pk": str(receive.pk),
            "source_identifier": receive.receive_identifier,
            "source_label_lower": receive._meta.label_lower,
            "source_model_name": receive._meta.verbose_name,
            "transaction_word": "confirmed",
        }
        return HttpResponseRedirect(
            reverse(
                "edc_pharmacy:confirm_stock_from_queryset_url",
                kwargs={"session_uuid": session_uuid},
            )
        )
