from __future__ import annotations

import ast
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..models import StockRequest, StockRequestItem
from ..utils import allocate_stock


@method_decorator(login_required, name="dispatch")
class AllocateToSubjectView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    model_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/allocate_to_subject.html"
    session_key = "model_pks"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get(self, request: WSGIRequest, *args, **kwargs):
        if not self.model_pks:
            self.model_pks = [kwargs.get("pk")]
        request.session[self.session_key] = json.dumps([str(pk) for pk in self.model_pks])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        stock_request_id = kwargs.get("stock_request_id")
        try:
            stock_request = StockRequest.objects.get(id=stock_request_id)
        except ObjectDoesNotExist:
            stock_request = None
            messages.add_message(self.request, messages.ERROR, "Invalid stock request.")
        kwargs.update(
            stock_request=stock_request,
            stock_request_changelist_url=self.stock_request_changelist_url(stock_request),
            object_count=len(self.model_pks),
            subject_identifiers=self.get_next_subject_identifiers(stock_request, 12),
        )
        return super().get_context_data(**kwargs)

    def get_next_subject_identifiers(
        self, stock_request: StockRequest, count: int | None = None
    ) -> list[str]:
        subject_identifiers = (
            StockRequestItem.objects.values_list(
                "registered_subject__subject_identifier", flat=True
            )
            .filter(stock_request=stock_request, allocation__stock_request_item__isnull=True)
            .order_by("registered_subject__subject_identifier")
        )
        if count:
            return [s for s in subject_identifiers[:count]]
        return [s for s in subject_identifiers]

    def stock_request_changelist_url(self, stock_request: StockRequest) -> str:
        if stock_request:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist")
            url = f"{url}?q={stock_request.request_identifier}"
            return url
        return ""

    def post(self, request, *args, **kwargs):
        codes = request.POST.getlist("codes")
        subject_identifiers = request.POST.get("subject_identifiers")
        subject_identifiers = ast.literal_eval(subject_identifiers)
        codes = dict(zip(codes, subject_identifiers))
        stock_request = StockRequest.objects.get(id=kwargs.get("stock_request_id"))
        allocated, not_allocated = allocate_stock(
            stock_request, codes, allocated_by=request.user.username
        )
        messages.add_message(
            request,
            messages.SUCCESS,
            f"Allocated {allocated} stock records. Skipped {not_allocated}.",
        )
        if self.get_next_subject_identifiers(stock_request):
            url = reverse(
                "edc_pharmacy:allocate_url",
                kwargs={"stock_request_id": kwargs.get("stock_request_id")},
            )
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(self.stock_request_changelist_url(stock_request))
