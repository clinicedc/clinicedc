from __future__ import annotations

import json

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

# TODO: WIP


@method_decorator(login_required, name="dispatch")
class SelectLabelConfigAndPrintView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    stock_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/select_label_config_and_print.html"
    session_key = "model_pks"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get(self, request: WSGIRequest, *args, **kwargs):
        if not self.stock_pks:
            self.stock_pks = [kwargs.get("pk")]
        request.session[self.session_key] = json.dumps([str(pk) for pk in self.stock_pks])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(
            object_count=len(self.stock_pks),
        )
        return super().get_context_data(**kwargs)

    @property
    def source_changelist_url(self):
        return reverse(
            f"edc_pharmacy_admin:edc_pharmacy_{self.kwargs.get("model")}_changelist"
        )

    @property
    def model_cls(self):
        return django_apps.get_model(f"edc_pharmacy.{self.kwargs.get("model")}")

    def post(self, request, *args, **kwargs):
        url = None
        return HttpResponseRedirect(url)
