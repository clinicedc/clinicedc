from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.handlers.wsgi import WSGIRequest

if TYPE_CHECKING:
    from edc_crf.model_mixins import CrfModelMixin
    from edc_identifier.model_mixins import UniqueSubjectIdentifierModelMixin
    from edc_pdf_reports import CrfPdfReport

    class ModelMixin(CrfModelMixin, UniqueSubjectIdentifierModelMixin):
        pdf_report_cls = None


class PdfReportModelMixin:
    pdf_report_cls: type[CrfPdfReport]

    def get_pdf_report(self: ModelMixin, request: WSGIRequest):
        return self.pdf_report_cls(model_obj=self, request=request, user=request.user)

    class Meta:
        abstract = True
