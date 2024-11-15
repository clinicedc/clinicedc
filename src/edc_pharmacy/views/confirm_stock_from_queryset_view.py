from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import Stock
from ..utils import confirm_stock


@method_decorator(login_required, name="dispatch")
class ConfirmStockFromQuerySetView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name: str = "edc_pharmacy/stock/confirm_stock_by_queryset.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        stock_count = (
            Stock.objects.values("pk").filter(pk__in=self.stock_pks, confirmed=False).count()
        )
        stock_count = 12 if stock_count > 12 else stock_count
        context = dict(
            stock_count=list(range(1, stock_count + 1)),
            source_changelist_url=self.source_changelist_url,
        )
        return context

    @property
    def source_changelist_url(self):
        return reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")

    @property
    def stock_pks(self):
        session_uuid = self.kwargs.get("session_uuid")
        return self.request.session[str(session_uuid)]

    def post(self, request, *args, **kwargs):
        codes = request.POST.getlist("codes")
        Stock.objects.values("pk").filter(pk__in=self.stock_pks, confirmed=False)
        confirmed, not_confirmed = confirm_stock(
            None, codes, None, confirmed_by=request.user.username
        )
        messages.add_message(
            request,
            messages.SUCCESS,
            f"Confirmed {confirmed} stock records. Skipped {not_confirmed}.",
        )
        if (
            Stock.objects.values("code")
            .filter(pk__in=self.stock_pks, confirmed=False)
            .exists()
        ):
            url = reverse("edc_pharmacy:confirm_stock_from_queryset_url", kwargs=kwargs)
        else:
            self.request.session[self.kwargs.get("session_uuid")] = None
            url = f"{self.source_changelist_url}?q="
        return HttpResponseRedirect(url)
