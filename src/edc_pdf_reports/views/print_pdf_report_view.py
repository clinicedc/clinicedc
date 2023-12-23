import json
from io import BytesIO

import mempass
from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin, View
from pypdf import PdfWriter

from ..numbered_canvas import NumberedCanvas


@method_decorator(login_required, name="dispatch")
class PrintPdfReportView(ContextMixin, View):
    """Download as PDF from the browser using Django's FileResponse.

    See also PdfIntermediateView and PdfReportModelMixin.
    """

    session_key = "model_pks"

    def get(self, request, *args, **kwargs):
        kwargs = self.get_context_data(**kwargs)
        return self.render_to_response(**kwargs)

    def post(self, request, *args, **kwargs):
        # accepts post data from form on intermediate page
        kwargs.update(phrase=request.POST.get("phrase"))
        return self.get(request, *args, **kwargs)

    def render_to_response(self, **kwargs) -> FileResponse | HttpResponseRedirect:
        """Render buffer to HTTP response"""
        merger = PdfWriter()
        try:
            model_pks = json.loads(self.request.session.pop(self.session_key))
        except KeyError:
            pass
        else:
            app_label, model_name = kwargs.get("app_label"), kwargs.get("model_name")
            for pk in model_pks:
                buffer = self.render_to_pdf(pk, app_label, model_name)
                merger.append(fileobj=buffer)
                buffer.close()
            new_buffer = BytesIO()
            password = kwargs.get("phrase") or slugify(mempass.mkpassword(2))
            merger.encrypt(password, algorithm="AES-256")
            merger.write(new_buffer)
            new_buffer.seek(0)
            report_filename = self.get_report_filename(model_pks, app_label, model_name)
            self.message_user(report_filename=report_filename, password=password)
            return FileResponse(new_buffer, as_attachment=True, filename=report_filename)
        messages.error(
            self.request,
            format_html(
                _("PDF report was not created because of an error. Please try again."),
                fail_silently=True,
            ),
        )
        return HttpResponseRedirect("/")

    def render_to_pdf(self, pk: str, app_label: str, model_name: str) -> BytesIO:
        model_obj = django_apps.get_model(app_label, model_name).objects.get(pk=pk)
        pdf_report = model_obj.pdf_report_cls(model_obj=model_obj, request=self.request)
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

    def get_report_filename(
        self, model_pks: list[str], app_label: str, model_name: str
    ) -> str:
        pdf_report_cls = django_apps.get_model(app_label, model_name).pdf_report_cls
        if len(model_pks) == 1:
            model_obj = django_apps.get_model(app_label, model_name).objects.get(
                pk=model_pks[0]
            )
            report_filename = model_obj.get_pdf_report(self.request).report_filename
        else:
            report_filename = pdf_report_cls.get_generic_report_filename()
        if not report_filename:
            raise ValueError("Cannot create file without a filename. Got report_filename=None")
        return report_filename

    def message_user(self, report_filename=None, password=None) -> None:
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
