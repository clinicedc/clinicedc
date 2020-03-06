from django.urls import path, include
from django.views.generic.base import View

urlpatterns = [
    path(r"edc_data_manager/", include("edc_data_manager.urls")),
    path(r"edc_pharmacy/", include("edc_pharmacy.urls")),
    path(r"edc_lab/", include("edc_lab.urls")),
    path(r"edc_locator/", include("edc_locator.urls")),
    path(r"edc_device/", include("edc_device.urls")),
    path(r"edc_adverse_event/", include("edc_adverse_event.urls")),
    path(r"edc_visit_schedule/", include("edc_visit_schedule.urls")),
    path(r"edc_navbar/", include("edc_navbar.urls")),
    path(r"edc_navbar/", include("edc_consent.urls")),
    path(r"edc_navbar/", include("edc_protocol.urls")),
    path(r"edc_adverse_event/", include("edc_adverse_event.urls")),
    path(r"edc_dashboard/", include("edc_dashboard.urls")),
    path(r"edc_export/", include("edc_export.urls")),
    path(r"", View.as_view(), name="navbar_one_url"),
    path(r"", View.as_view(), name="navbar_two_url"),
    path(r"", View.as_view(), name="logout"),
    path(r"", View.as_view(), name="administration_url"),
    path(r"", View.as_view(), name="home_url"),
]
