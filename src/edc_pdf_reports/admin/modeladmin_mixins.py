from django.contrib.admin import display
from django.template.loader import render_to_string


class PdfButtonModelAdminMixin:
    """A model admin mixin to add a PDF download button for
    the model's custom `CrfPdfReport`.

    Add "pdf_button" to the changelist's `list_display`
    """

    pdf_button_url_name: str = "edc_pdf_reports:pdf_intermediate_url"
    pdf_button_title: str = "Download report as PDF"
    pdf_button_template_name: str = "edc_pdf_reports/pdf_button.html"

    @display(description="PDF")
    def pdf_button(self, obj):
        context = dict(
            str_pk=str(obj.id),
            app_label=obj._meta.app_label,
            model_name=obj._meta.model_name,
            title=self.pdf_button_title,
            url_name=self.pdf_button_url_name,
        )
        return render_to_string(template_name=self.pdf_button_template_name, context=context)
