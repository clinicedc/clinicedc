from __future__ import annotations

import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

template_name = getattr(
    settings,
    "EDC_PDF_REPORTS_TEMPLATES",
    {"pdf_intermediate": "edc_pdf_reports/pdf_intermediate_edc.html"},
)


@method_decorator(login_required, name="dispatch")
class IntermediateView(EdcViewMixin, EdcProtocolViewMixin, TemplateView):
    model_pks: list[str] | None = None
    template_name: str = template_name.get("update_label_config_intermediate")
    session_key = "model_pks"

    def get(self, request: WSGIRequest, *args, **kwargs):
        if not self.model_pks:
            self.model_pks = [kwargs.get("pk")]
        request.session[self.session_key] = json.dumps([str(pk) for pk in self.model_pks])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(
            object_count=len(self.model_pks),
            # report_name=model_cls._meta.verbose_name,
            # url=self.get_pdf_report_url(app_label, model_name),
            return_to_changelist_url=reverse(
                "edc_pharmacy_admin:edc_pharmacy_stock_changelist"
            ),
            label_configuration_name="",
        )
        return super().get_context_data(**kwargs)
