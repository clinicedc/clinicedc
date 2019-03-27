from django.contrib import admin
from django.urls.conf import path, include
from dashboard_app.admin_site import dashboard_app_admin
from edc_lab.admin_site import edc_lab_admin

from .views import HomeView

app_name = "edc_review_dashboard"


urlpatterns = []

for app_name in [
    "edc_base",
    "edc_consent",
    "edc_device",
    "edc_protocol",
    "edc_reference",
    "edc_visit_schedule",
]:
    urlpatterns.append(path(f"{app_name}/", include(f"{app_name}.urls")))


urlpatterns += [
    path("admin/", admin.site.urls),
    path("admin/", dashboard_app_admin.urls),
    path("admin/", edc_lab_admin.urls),
    path("", include("edc_subject_dashboard.urls")),
    path("", include("edc_lab_dashboard.urls")),
    path("", include("dashboard_app.urls")),
    path("", HomeView.as_view(), name="logout"),
    path("", HomeView.as_view(), name="administration_url"),
    path("", HomeView.as_view(), name="home_url"),
]
