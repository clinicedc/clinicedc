from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import Stock
from ..utils import confirm_stock

if TYPE_CHECKING:
    from ..models import Receive, RepackRequest


@method_decorator(login_required, name="dispatch")
class ConfirmStockView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    stock_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/confirm_stock.html"
    session_key = "model_pks"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get(self, request: WSGIRequest, *args, **kwargs):
        if not self.stock_pks:
            self.stock_pks = [kwargs.get("pk")]
        request.session[self.session_key] = json.dumps([str(pk) for pk in self.stock_pks])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        dct = self.get_values_dict(**kwargs)
        confirmed_count = (
            Stock.objects.values("code")
            .filter(**{dct.get("fk_attr"): dct.get("obj").id, "confirmed": True})
            .count()
        )

        kwargs.update(
            object_count=len(self.stock_pks),
            source_identifier=dct.get("source_identifier"),
            source_model_name=self.model_cls._meta.verbose_name,
            source_changelist_url=self.source_changelist_url,
            source_pk=self.kwargs.get("source_pk"),
            item_count=list(range(1, 13)),
            confirmed_count=confirmed_count,
            confirmed_codes=self.get_confirmed_codes(dct.get("obj"), dct.get("fk_attr")),
        )
        return super().get_context_data(**kwargs)

    def get_values_dict(self, **kwargs) -> dict:
        values_dict = {}
        obj = self.model_cls.objects.get(pk=kwargs.get("source_pk"))
        values_dict.update(obj=obj)
        try:
            values_dict.update(source_identifier=obj.repack_identifier)
            values_dict.update(fk_attr="repack_request")
        except AttributeError:
            values_dict.update(source_identifier=obj.receive_identifier)
            values_dict.update(fk_attr="receive_item__receive")
        return values_dict

    def get_confirmed_codes(self, obj: RepackRequest | Receive, fk_attr: str) -> list[str]:
        return Stock.objects.values_list("code", flat=True).filter(
            **{fk_attr: obj.id, "confirmed": True}
        )

    @property
    def source_changelist_url(self):
        return reverse(
            f"edc_pharmacy_admin:edc_pharmacy_{self.kwargs.get("model")}_changelist"
        )

    @property
    def model_cls(self):
        return django_apps.get_model(f"edc_pharmacy.{self.kwargs.get("model")}")

    def post(self, request, *args, **kwargs):
        dct = self.get_values_dict(**kwargs)
        codes = request.POST.getlist("codes")
        confirmed, not_confirmed = confirm_stock(
            dct.get("obj"), codes, dct.get("fk_attr"), confirmed_by=request.user.username
        )
        messages.add_message(
            request,
            messages.SUCCESS,
            f"Confirmed {confirmed} stock records. Skipped {not_confirmed}.",
        )
        if (
            Stock.objects.values("code")
            .filter(**{dct.get("fk_attr"): dct.get("obj").id, "confirmed": False})
            .exists()
        ):
            url = reverse("edc_pharmacy:confirm_stock_url", kwargs=kwargs)
        else:
            url = f"{self.source_changelist_url}?q={dct.get("obj").pk}"
        return HttpResponseRedirect(url)
