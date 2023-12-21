from django.contrib import admin
from django.urls import path
from edc_adverse_event.pdf_reports import DeathPdfReport
from edc_adverse_event.utils import get_ae_model_name

from edc_pdf_reports.views import PrintPdfReportView

urlpatterns = [
    path("admin/", admin.site.urls),
]
