"""Repack workflow — per-request page with Process / Print labels / Confirm actions."""

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
from edc_utils.celery import run_task_sync_or_async

from ..models import RepackRequest, Stock
from ..utils import process_repack_request_queryset
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class RepackView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/repack.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def _get_repack_request(self) -> RepackRequest:
        return get_object_or_404(RepackRequest, pk=self.kwargs["repack_request"])

    @staticmethod
    def _stock_counts(rr: RepackRequest) -> tuple[int, int]:
        qs = Stock.objects.filter(repack_request=rr)
        confirmed = qs.filter(confirmed=True).count()
        unconfirmed = qs.filter(confirmed=False).count()
        return confirmed, unconfirmed

    def get_context_data(self, **kwargs):
        kwargs.pop("repack_request", None)
        context = super().get_context_data(**kwargs)
        rr = self._get_repack_request()
        confirmed_qty, unconfirmed_qty = self._stock_counts(rr)
        context.update(
            repack_request=rr,
            confirmed_qty=confirmed_qty,
            unconfirmed_qty=unconfirmed_qty,
        )
        return context

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        rr = self._get_repack_request()
        action = request.POST.get("action")
        redirect_url = reverse(
            "edc_pharmacy:repack_url", kwargs={"repack_request": rr.pk}
        )

        if action == "process":
            return self._handle_process(request, rr, redirect_url)
        if action == "print_labels":
            return self._handle_print_labels(request, rr, redirect_url)
        if action == "confirm_stock":
            return self._handle_confirm_stock(request, rr, redirect_url)

        return HttpResponseRedirect(redirect_url)

    @staticmethod
    def _handle_process(request, rr: RepackRequest, redirect_url: str) -> HttpResponseRedirect:
        if (rr.item_qty_processed or 0) > 0:
            messages.warning(request, "This repack request has already been processed.")
            return HttpResponseRedirect(redirect_url)
        task = run_task_sync_or_async(
            process_repack_request_queryset,
            repack_request_pks=[rr.pk],
            username=request.user.username,
        )
        task_id = getattr(task, "id", None)
        RepackRequest.objects.filter(pk=rr.pk).update(task_id=task_id)
        if task_id:
            messages.info(request, f"Processing in background (task {task_id}).")
        else:
            messages.success(request, f"Repack request {rr.repack_identifier} processed.")
        return HttpResponseRedirect(redirect_url)

    @staticmethod
    def _handle_print_labels(
        request, rr: RepackRequest, redirect_url: str
    ) -> HttpResponseRedirect:
        stock_pks = list(
            Stock.objects.filter(repack_request=rr).values_list("pk", flat=True)
        )
        if not stock_pks:
            messages.warning(request, "No stock items found. Process the request first.")
            return HttpResponseRedirect(redirect_url)
        session_uuid = str(uuid4())
        request.session[session_uuid] = [str(pk) for pk in stock_pks]
        return HttpResponseRedirect(
            reverse(
                "edc_pharmacy:print_labels_url",
                kwargs={"session_uuid": session_uuid, "model": "stock"},
            )
        )

    @staticmethod
    def _handle_confirm_stock(
        request, rr: RepackRequest, redirect_url: str
    ) -> HttpResponseRedirect:
        stock_qs = Stock.objects.filter(repack_request=rr, confirmed=False)
        stock_codes = list(stock_qs.values_list("code", flat=True))
        if not stock_codes:
            messages.warning(request, "All stock items are already confirmed.")
            return HttpResponseRedirect(redirect_url)
        session_uuid = str(uuid4())
        request.session[session_uuid] = {
            "stock_codes": stock_codes,
            "source_pk": str(rr.pk),
            "source_identifier": rr.repack_identifier,
            "source_label_lower": rr._meta.label_lower,
            "source_model_name": rr._meta.verbose_name,
            "transaction_word": "confirmed",
        }
        return HttpResponseRedirect(
            reverse(
                "edc_pharmacy:confirm_stock_from_queryset_url",
                kwargs={"session_uuid": session_uuid},
            )
        )
