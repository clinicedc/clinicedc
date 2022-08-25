from django.urls.conf import path
from django.views.generic import RedirectView
from edc_dashboard.views import AdministrationView
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

from review_dashboard_app.admin_site import review_dashboard_app_admin

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
    "review_dashboard_app",
]:
    for p in paths_for_urlpatterns(app_name):
        urlpatterns.append(p)

urlpatterns += [
    path("admin/", review_dashboard_app_admin.urls),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
    path("", RedirectView.as_view(url="admin/"), name="logout"),
]
