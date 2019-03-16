from django.contrib import admin
from django.urls import path
from edc_dashboard.url_config import UrlConfig
from edc_dashboard.views import DashboardView as BaseDashboardView


class DashboardView(BaseDashboardView):

    dashboard_url = "subject_dashboard_url"
    dashboard_template = "subject_dashboard_template"


urlpatterns = [path("admin/", admin.site.urls)]

subject_dashboard_url_config = UrlConfig(
    url_name="subject_dashboard_url",
    view_class=DashboardView,
    label="subject_dashboard",
    identifier_label="subject_identifier",
    identifier_pattern="\w+",
)

urlpatterns += subject_dashboard_url_config.dashboard_urls
