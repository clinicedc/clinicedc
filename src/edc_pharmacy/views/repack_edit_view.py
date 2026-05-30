"""Repack workflow — create or edit a RepackRequest."""

from __future__ import annotations

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

from ..forms.stock import RepackEditForm
from ..models import RepackRequest
from .auths_view_mixin import PharmacistRequiredMixin


@method_decorator(login_required, name="dispatch")
class RepackEditView(
    PharmacistRequiredMixin, EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name = "edc_pharmacy/stock/repack_edit.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def _get_instance(self) -> RepackRequest | None:
        pk = self.kwargs.get("repack_request")
        if pk:
            return get_object_or_404(RepackRequest, pk=pk)
        return None

    def get_context_data(self, form=None, **kwargs):
        kwargs.pop("repack_request", None)
        instance = self._get_instance()
        form = form or RepackEditForm(instance=instance)
        return super().get_context_data(instance=instance, form=form, **kwargs)

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        instance = self._get_instance()
        data = request.POST.copy()
        if instance and (instance.item_qty_processed or 0) > 0:
            data["stock_code"] = instance.from_stock.code
            data["container"] = str(instance.container.pk)
            data["item_qty_repack"] = str(instance.item_qty_repack)
        form = RepackEditForm(data, instance=instance)
        if form.is_valid():
            cd = form.cleaned_data
            from_stock = cd["from_stock"]
            container = cd["container"]
            container_unit_qty = cd.get("container_unit_qty") or container.unit_qty_default
            if instance is None:
                obj = RepackRequest(
                    from_stock=from_stock,
                    container=container,
                    container_unit_qty=container_unit_qty,
                    override_container_unit_qty=cd.get("override_container_unit_qty", False),
                    item_qty_repack=cd["item_qty_repack"],
                    user_created=request.user.username,
                    user_modified=request.user.username,
                )
                obj.save()
                messages.success(
                    request, f"Repack request {obj.repack_identifier} created."
                )
            else:
                instance.container_unit_qty = container_unit_qty
                instance.override_container_unit_qty = cd.get(
                    "override_container_unit_qty", False
                )
                instance.item_qty_repack = cd["item_qty_repack"]
                instance.user_modified = request.user.username
                instance.save()
                obj = instance
                messages.success(
                    request, f"Repack request {obj.repack_identifier} updated."
                )
            return HttpResponseRedirect(
                reverse("edc_pharmacy:repack_url", kwargs={"repack_request": obj.pk})
            )
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
