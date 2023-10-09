from django.urls.conf import include, path
from django.views.generic import RedirectView
from edc_dashboard.views import AdministrationView
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

app_name = "review_dashboard_app"


urlpatterns = []

for app_name in [
    "edc_action_item",
    "edc_appointment",
    "edc_consent",
    "edc_dashboard",
    "edc_data_manager",
    "edc_device",
    "edc_lab",
    "edc_lab_dashboard",
    "edc_locator",
    "edc_protocol",
    "edc_reference",
    "edc_subject_dashboard",
    "edc_visit_schedule",
    "edc_visit_tracking",
    "review_dashboard_app",
]:
    for p in paths_for_urlpatterns(app_name):
        urlpatterns.append(p)

urlpatterns += [
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
    path("", RedirectView.as_view(url="admin/"), name="logout"),
]
