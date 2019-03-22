from django.contrib import admin
from django.urls import path, include

from .views import HomeView

app_name = "edc_review_dashboard"

urlpatterns = [
    #     path("accounts/", include("edc_auth.urls")),
    #     path("admin/", include("edc_auth.urls")),
    path("admin/", admin.site.urls),
    path("", include("edc_base.urls")),
    path("", include("edc_device.urls")),
    path("", include("edc_protocol.urls")),
    path("", include("edc_reference.urls")),
    path("", include("edc_search.urls")),
    path("", include("edc_review_dashboard.tests.dashboard_app.urls")),
    path("", HomeView.as_view(), name="home_url"),
    path("", HomeView.as_view(), name="administration_url")]
