from django.urls import path
from django.views.generic.base import RedirectView, View
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

urlpatterns = []

for app_name in [
    "edc_auth",
    "edc_data_manager",
    "edc_pharmacy",
    "edc_lab",
    "edc_locator",
    "edc_device",
    "edc_adverse_event",
    "edc_visit_schedule",
    "edc_navbar",
    "edc_consent",
    "edc_protocol",
    "edc_dashboard",
    "edc_export",
    "edc_reference",
]:
    for p in paths_for_urlpatterns(app_name):
        urlpatterns.append(p)

urlpatterns += [
    path(r"", View.as_view(), name="navbar_one_url"),
    path(r"", View.as_view(), name="navbar_two_url"),
    path("", RedirectView.as_view(url="admin/"), name="administration_url"),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
    path("", RedirectView.as_view(url="admin/"), name="logout"),
]
