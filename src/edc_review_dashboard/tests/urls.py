from django.contrib import admin
from django.urls.conf import include, path
from edc_action_item.admin_site import edc_action_item_admin
from edc_appointment.admin_site import edc_appointment_admin
from edc_data_manager.admin_site import edc_data_manager_admin
from edc_lab.admin_site import edc_lab_admin
from edc_locator.admin_site import edc_locator_admin

from review_dashboard_app.admin_site import review_dashboard_app_admin

from .views import HomeView

app_name = "review_dashboard_app"


urlpatterns = []

for app_name in [
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
]:
    urlpatterns.append(path(f"{app_name}/", include(f"{app_name}.urls")))


urlpatterns += [
    path("accounts/", include("edc_auth.urls")),
    path("admin/", include("edc_auth.urls")),
    path("admin/", admin.site.urls),
    path("admin/", review_dashboard_app_admin.urls),
    path("admin/", edc_action_item_admin.urls),
    path("admin/", edc_lab_admin.urls),
    path("admin/", edc_appointment_admin.urls),
    path("admin/", edc_locator_admin.urls),
    path("admin/", edc_data_manager_admin.urls),
    path("review_dashboard_app/", include("review_dashboard_app.urls")),
    path("", HomeView.as_view(), name="logout"),
    path("", HomeView.as_view(), name="administration_url"),
    path("", HomeView.as_view(), name="home_url"),
]
