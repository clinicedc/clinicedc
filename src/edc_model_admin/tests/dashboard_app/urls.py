from edc_dashboard.url_config import UrlConfig

from .views import DashboardView

app_name = "dashboard_app"

subject_dashboard_url_config = UrlConfig(
    url_name="subject_dashboard_url",
    namespace=app_name,
    view_class=DashboardView,
    label="subject_dashboard",
    identifier_label="subject_identifier",
    identifier_pattern="\w+",
)

urlpatterns = subject_dashboard_url_config.dashboard_urls
