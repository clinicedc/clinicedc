from __future__ import annotations

import json

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

from edc_pharmacy.models import Allocation

# class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
#     template_name = f"meta_edc/bootstrap{get_bootstrap_version()}/home.html"
#     navbar_name = settings.APP_NAME
#     navbar_selected_item = "home"


@method_decorator(login_required, name="dispatch")
class RelabelView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    model_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/relabel.html"
    session_key = "model_pks"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get(self, request: WSGIRequest, *args, **kwargs):
        if not self.model_pks:
            self.model_pks = [kwargs.get("pk")]
        request.session[self.session_key] = json.dumps([str(pk) for pk in self.model_pks])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        allocation_identifier = kwargs.get("allocation_identifier")
        try:
            allocation = Allocation.objects.get(allocation_identifier=allocation_identifier)
        except Allocation.DoesNotExist:
            allocation = None
            messages.add_message(
                self.request,
                messages.ERROR,
                f"Invalid fulfillment identifier. Got {allocation_identifier}.",
            )
        kwargs.update(
            allocation=allocation,
            allocation_changelist_url=self.allocation_changelist_url(allocation),
            object_count=len(self.model_pks),
            return_to_changelist_url=self.allocation_changelist_url(allocation),
            item_count=list(range(1, 13)),
        )
        return super().get_context_data(**kwargs)

    def allocation_changelist_url(self, allocation: Allocation) -> str:
        if allocation:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_allocation_changelist")
            url = f"{url}?q={allocation.allocation_identifier}"
            return url
        return ""

    def post(self, request, *args, **kwargs):
        # update model
        # blah blah
        url = reverse("edc_pharmacy:relabel", args=("000003",))
        return HttpResponseRedirect(url)
