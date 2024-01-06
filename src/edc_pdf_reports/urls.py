from django.urls import path

from .views import PdfIntermediateView, PrintPdfReportView

app_name = "edc_pdf_reports"

urlpatterns = [
    path(
        "pdf_report/intermediate/<app_label>/<model_name>/<pk>/",
        PdfIntermediateView.as_view(),
        name="pdf_intermediate_url",
    ),
    path(
        "pdf_report/<app_label>/<model_name>/<pk>/",
        PrintPdfReportView.as_view(),
        name="pdf_report_url",
    ),
    path(
        "pdf_report/<app_label>/<model_name>/",
        PrintPdfReportView.as_view(),
        name="pdf_report_url",
    ),
]
