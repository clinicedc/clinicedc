from __future__ import annotations

import json

import mempass
from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin


@method_decorator(login_required, name="dispatch")
class PdfIntermediateView(EdcViewMixin, EdcProtocolViewMixin, TemplateView):
    model_pks: list[str] | None = None
    template_name: str = "edc_pdf_reports/pdf_intermediate.html"
    pdf_report_url_name = "edc_pdf_reports:pdf_report_url"
    session_key = "model_pks"

    def get(self, request: WSGIRequest, *args, **kwargs):
        if not self.model_pks:
            self.model_pks = [kwargs.get("pk")]
        request.session[self.session_key] = json.dumps([str(pk) for pk in self.model_pks])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, app_label: str = None, model_name: str = None, **kwargs):
        model_cls = django_apps.get_model(app_label, model_name)
        kwargs.update(
            object_count=len(self.model_pks),
            report_name=model_cls._meta.verbose_name,
            url=self.get_pdf_report_url(app_label, model_name),
            return_to_changelist_url=reverse(model_cls.pdf_report_cls.changelist_url),
            phrase=slugify(mempass.mkpassword(2)),
        )
        return super().get_context_data(**kwargs)

    def get_pdf_report_url(self, app_label: str, model_name: str) -> str:
        return reverse(
            self.pdf_report_url_name,
            kwargs=dict(app_label=app_label, model_name=model_name),
        )
