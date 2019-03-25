# from django.contrib import admin
# from django.urls import path, include
# from dashboard_app.admin_site import dashboard_app_admin
#
# from .views import HomeView
#
# app_name = "edc_review_dashboard"
#
# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("admin/", dashboard_app_admin.urls),
#     path("", include("edc_base.urls")),
#     path("", include("edc_device.urls")),
#     path("", include("edc_protocol.urls")),
#     path("", include("edc_reference.urls")),
#     path("", include("edc_search.urls")),
#     path("", include("edc_subject_dashboard.urls")),
#     path("", HomeView.as_view(), name="home_url"),
#     path("", HomeView.as_view(), name="administration_url")]

from django.contrib import admin
from django.urls.conf import path, include
from dashboard_app.admin_site import dashboard_app_admin
from edc_lab.admin_site import edc_lab_admin


app_name = "edc_review_dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/", dashboard_app_admin.urls),
    path("admin/", edc_lab_admin.urls),
    path("", include("edc_subject_dashboard.urls")),
    path("", include("edc_lab_dashboard.urls")),
    path("", include("dashboard_app.urls"))
]
