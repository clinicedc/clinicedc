from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

from .admin import *  # noqa
from .views import CrfOneListView

app_name = "edc_model_admin"

urlpatterns = []

for app_name in [
    "edc_dashboard",
    "edc_consent",
    "edc_device",
    "edc_protocol",
    "edc_reference",
    "edc_visit_schedule",
]:
    urlpatterns.append(path(f"{app_name}/", include(f"{app_name}.urls")))

urlpatterns += [
    path("admin/", admin.site.urls),
    path("", CrfOneListView.as_view(), name="crfone-list"),
    path("", include("edc_model_admin.tests.dashboard_app.urls")),
    path("", include("edc_model_admin.tests.dashboard2_app.urls")),
    path("", RedirectView.as_view(url="admin/"), name="administration_url"),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
    path("", RedirectView.as_view(url="admin/"), name="logout"),
]
