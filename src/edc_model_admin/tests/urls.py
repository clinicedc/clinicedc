from django.contrib import admin
from django.urls import path
from edc_dashboard.url_config import UrlConfig

from .views import CrfOneListView, DashboardView

app_name = "edc_model_admin"


subject_dashboard_url_config = UrlConfig(
    url_name="subject_dashboard_url",
    view_class=DashboardView,
    label="subject_dashboard",
    identifier_label="subject_identifier",
    identifier_pattern="\w+",
)

urlpatterns = subject_dashboard_url_config.dashboard_urls
urlpatterns += [
    path("admin/", admin.site.urls),
    path("", CrfOneListView.as_view(), name="crfone-list"),
]
