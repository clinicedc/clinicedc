from django.contrib import admin
from django.urls.conf import include, path
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

from data_manager_app.admin_site import data_manager_app_admin

from .views import HomeView

app_name = "edc_data_manager"


urlpatterns = []

for app_name in [
    "edc_auth",
    "edc_action_item",
    "edc_appointment",
    "edc_consent",
    "edc_dashboard",
    "edc_data_manager",
    "edc_device",
    "edc_lab_dashboard",
    "edc_protocol",
    "edc_reference",
    "edc_subject_dashboard",
    "edc_visit_schedule",
    "data_manager_app",
]:
    for p in paths_for_urlpatterns(app_name):
        urlpatterns.append(p)


urlpatterns += [
    path("data_manager_app_admin/", data_manager_app_admin.urls),
    path("accounts/", include("edc_auth.urls")),
    path("edc_auth/", include("edc_auth.urls")),
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="administration_url"),
    path("", HomeView.as_view(), name="home_url"),
]
