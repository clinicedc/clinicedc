import json
from io import BytesIO

import mempass
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin, TemplateView, View
from edc_dashboard.view_mixins import EdcViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin
from pypdf import PdfWriter

from .numbered_canvas import NumberedCanvas


@method_decorator(login_required, name="dispatch")
class PdfIntermediateView(EdcViewMixin, EdcProtocolViewMixin, TemplateView):
    pdf_report_cls = None
    pks: list[str] | None = None
    template_name = "edc_pdf_reports/pdf_intermediate.html"

    def get(self, request, *args, **kwargs):
        if not self.pks:
            self.pks = [kwargs.get("pk")]
        request.session["report_pks"] = json.dumps([str(pk) for pk in self.pks])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(
            object_count=len(self.pks),
            report_name=self.pdf_report_cls.get_verbose_name(),
            url=reverse(f"pdf_{self.pdf_report_cls.name}s_url"),
            return_to_changelist_url=reverse(self.pdf_report_cls.changelist_url),
            phrase=slugify(mempass.mkpassword(2)),
        )
        return super().get_context_data(**kwargs)


@method_decorator(login_required, name="dispatch")
class PrintPdfReportView(ContextMixin, View):
    """Download as PDF from the browser using Django's FileResponse.

    Link this view to urls. For example:
        Given a reportlab class `DeathPdfReport`

        path(
            "pdf_report/deathreport/<pk>/",
            PrintPdfReportView.as_view(pdf_report_cls=DeathPdfReport),
            name="pdf_death_report_url",
        ),
        ...

    See also PdfButtonModelAdminMixin.
    """

    pdf_report_cls = None  # set in url

    def get(self, request, *args, **kwargs):
        kwargs = self.get_context_data(**kwargs)
        return self.render_to_response(**kwargs)

    def post(self, request, *args, **kwargs):
        # accepts post data from intermediate page
        kwargs.update(phrase=request.POST.get("phrase"))
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        pks = json.loads(self.request.session.pop("report_pks"))
        kwargs.update(pks=pks)
        return super().get_context_data(**kwargs)

    def render_to_response(self, **kwargs):
        """Render buffer to HTTP response"""
        pdf_report = None
        merger = PdfWriter()
        pks = kwargs.get("pks")
        for pk in pks:
            pdf_report = self.pdf_report_cls(
                pk=pk, user=self.request.user, request=self.request
            )
            buffer = self.render_to_buffer(pdf_report, **kwargs)
            merger.append(fileobj=buffer)
            buffer.close()
        new_buffer = BytesIO()
        password = kwargs.get("phrase") or slugify(mempass.mkpassword(2))
        merger.encrypt(password, algorithm="AES-256")
        merger.write(new_buffer)
        new_buffer.seek(0)
        report_filename = (
            pdf_report.report_filename if len(pks) == 1 else pdf_report.multi_report_filename
        )
        if not report_filename:
            raise ValueError("Cannot create file without a filename. Got report_filename=None")
        self.message_user(report_filename=report_filename, password=password, **kwargs)
        return FileResponse(new_buffer, as_attachment=True, filename=report_filename)

    @staticmethod
    def render_to_buffer(pdf_report=None, **kwargs):
        buffer = BytesIO()
        doctemplate = pdf_report.document_template(buffer, **pdf_report.page)
        story = pdf_report.get_report_story()
        doctemplate.build(
            story,
            onFirstPage=pdf_report.on_first_page,
            onLaterPages=pdf_report.on_later_pages,
            canvasmaker=NumberedCanvas,
        )
        buffer.seek(0)
        return buffer

    def message_user(self, report_filename=None, password=None, **kwargs):
        messages.success(
            self.request,
            format_html(
                _(
                    "The report has been exported as a secure PDF. See downloads in "
                    "your browser. %(br)sFile: %(report_filename)s %(br)s"
                    "Pass-phrase: %(password)s"
                )
                % dict(report_filename=report_filename, password=password, br="<BR>"),
                fail_silently=True,
            ),
        )

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
