"""Stock request workflow — create or edit a StockRequest."""

from __future__ import annotations

from datetime import datetime, time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..forms.stock import StockRequestEditForm
from ..models import StockRequest
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class StockRequestEditView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/stock_request_edit.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def _get_instance(self) -> StockRequest | None:
        pk = self.kwargs.get("stock_request")
        if pk:
            return get_object_or_404(StockRequest, pk=pk)
        return None

    def get_context_data(self, form=None, **kwargs):
        kwargs.pop("stock_request", None)
        instance = self._get_instance()
        form = form or StockRequestEditForm(instance=instance)
        return super().get_context_data(instance=instance, form=form, **kwargs)

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        instance = self._get_instance()
        form = StockRequestEditForm(request.POST, instance=instance)
        if form.is_valid():
            cd = form.cleaned_data
            tz = timezone.get_current_timezone()
            obj = form.save(commit=False)
            obj.request_datetime = datetime.combine(
                cd["request_date"], time.min
            ).replace(tzinfo=tz)
            start_date = cd.get("start_date")
            obj.start_datetime = (
                datetime.combine(start_date, time.min).replace(tzinfo=tz)
                if start_date
                else None
            )
            obj.cutoff_datetime = datetime.combine(
                cd["cutoff_date"], time.min
            ).replace(tzinfo=tz)
            if not instance:
                obj.user_created = request.user.username
            obj.user_modified = request.user.username
            obj.save()
            verb = "created" if not instance else "updated"
            messages.success(request, f"Stock request {obj.request_identifier} {verb}.")
            return HttpResponseRedirect(
                reverse("edc_pharmacy:stock_request_url", kwargs={"stock_request": obj.pk})
            )
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
