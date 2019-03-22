from edc_dashboard.url_config import UrlConfig

from .views import DashboardView

app_name = "dashboard2_app"

dashboard2_url_config = UrlConfig(
    url_name="dashboard_url",
    view_class=DashboardView,
    label="dashboard",
    identifier_label="subject_identifier",
    identifier_pattern="\w+",
)

urlpatterns = dashboard2_url_config.dashboard_urls
