from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from edc_label.views.print_setup_view import PrinterSetupView

from .views import BrowserPrintLabelsView, ChangePrinterView, HomeView, PrintLabelView

app_name = "edc_label"

urlpatterns = [
    path(
        r"browser_print_labels",
        BrowserPrintLabelsView.as_view(),
        name="browser_print_labels_url",
    ),
    re_path(
        r"printer/change/(?P<printer_type>\w+)/",
        ChangePrinterView.as_view(),
        name="change_session_printer",
    ),
    re_path(
        r"print/label/(?P<printer_name>\w+)/(?P<label_template_name>)\w+/",
        PrintLabelView.as_view(),
        name="print_label",
    ),
    path("print/label/", PrintLabelView.as_view(), name="print_label"),
    path(
        "print_server/change/",
        ChangePrinterView.as_view(),
        name="change_session_print_server",
    ),
    re_path(
        r"print/(?P<label_name>\w+)/"
        r"(?P<copies>\d+)/(?P<app_label>\w+)/"
        r"(?P<model_name>\w+)/"
        r"(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?"
        r"[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$",
        HomeView.as_view(),
        name="print-test-label",
    ),
    re_path(r"print/(?P<label_name>\w+)/$", HomeView.as_view(), name="print-test-label"),
    path("printer_setup/", PrinterSetupView.as_view(), name="printer_setup_url"),
    path("", HomeView.as_view(), name="home_url"),
]

if settings.APP_NAME == "edc_label":
    url_patterns = urlpatterns + [
        path("accounts/", include("edc_auth.urls")),
        path("admin/", admin.site.urls),
    ]
