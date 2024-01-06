import json

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

from ..utils import write_queryset_to_secure_pdf


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
        """Render PDF buffer to FileResponse."""
        try:
            model_pks = json.loads(self.request.session.pop(self.session_key))
        except KeyError as e:
            # TODO: is this needed?
            messages.error(
                self.request,
                format_html(
                    _(
                        f"PDF report was not created because of an error. Got {e}. "
                        "Please try again."
                    ),
                    fail_silently=True,
                ),
            )
        else:
            password = kwargs.get("phrase") or slugify(mempass.mkpassword(2))
            app_label, model_name = kwargs.get("app_label"), kwargs.get("model_name")
            qs = django_apps.get_model(app_label, model_name).objects.filter(pk__in=model_pks)
            buffer = write_queryset_to_secure_pdf(
                queryset=qs, password=password, request=self.request
            )
            report_filename = self.get_report_filename(model_pks, app_label, model_name)
            self.message_user(report_filename=report_filename, password=password)
            return FileResponse(buffer, as_attachment=True, filename=report_filename)
        return HttpResponseRedirect("/")

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
