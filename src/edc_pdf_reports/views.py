from io import BytesIO
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin, View
from pypdf import PdfWriter

from .numbered_canvas import NumberedCanvas


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

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def render_to_response(self, **kwargs):
        """Render buffer to HTTP response"""
        pdf_report = None
        merger = PdfWriter()
        pks = kwargs.get("pks") or [kwargs.get("pk")]
        for pk in pks:
            pdf_report = self.pdf_report_cls(
                pk=pk, user=self.request.user, request=self.request
            )
            buffer = self.render_to_buffer(pdf_report, **kwargs)
            merger.append(fileobj=buffer)
            buffer.close()
        new_buffer = BytesIO()
        merger.write(new_buffer)
        new_buffer.seek(0)
        report_filename = (
            pdf_report.report_filename if len(pks) == 1 else pdf_report.multi_report_filename
        )
        self.message_user(**kwargs)
        return FileResponse(
            new_buffer, as_attachment=True, filename=report_filename or f"{uuid4()}.pdf"
        )

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

    def message_user(self, **kwargs):
        report_filename = kwargs.get("report_filename")
        messages.success(
            self.request,
            _(
                "The report has been exported as a PDF. See downloads in your browser. "
                "The filename is '%(report_filename)s'."
            )
            % dict(report_filename=report_filename),
            fail_silently=True,
        )

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
