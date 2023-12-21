from django.contrib.admin import display
from django.template.loader import render_to_string


class PdfButtonModelAdminMixin:

    """A model admin mixin to add a PDF download button for
    the model objects custom `CrfPdfReport`.

    Add "pdf_button" to the changelist's `list_display`

    Link to view in urls. For example:
        Given a reportlab class `DeathPdfReport`

        path(
            "pdf_report/deathreport/<pk>/",
            PrintPdfReportView.as_view(pdf_report_cls=DeathPdfReport),
            name="pdf_death_report_url",
        ),
        ...

    where `name` is `pdf_button_url_name` on this class.

    See also `PrintPdfReportView` in `edc_pdf_reports`.
    """

    pdf_button_url_name: str
    pdf_button_title: str = "Download report as PDF"
    pdf_button_template_name: str = "edc_pdf_reports/pdf_button.html"

    @display(description="PDF", ordering="subject_identifier")
    def pdf_button(self, obj):
        context = dict(
            str_pk=str(obj.id),
            title=self.pdf_button_title,
            url_name=self.pdf_button_url_name,
        )
        return render_to_string(template_name=self.pdf_button_template_name, context=context)
