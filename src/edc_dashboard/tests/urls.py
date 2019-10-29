from django.urls.conf import path, include
from django.views.generic.base import RedirectView
from edc_dashboard.url_config import UrlConfig
from edc_dashboard.views import AdministrationView, ListboardView

from .admin import edc_dashboard_admin

app_name = "edc_dashboard"

subject_listboard_url_config = UrlConfig(
    url_name="listboard_url",
    namespace=app_name,
    view_class=ListboardView,
    label="subject_listboard",
    identifier_label="subject_identifier",
    identifier_pattern="/w+",
)

urlpatterns = subject_listboard_url_config.listboard_urls + [
    path("admin/", edc_dashboard_admin.urls),
    path("edc_auth/", include("edc_auth.urls")),
    path("edc_adverse_event/", include("edc_adverse_event.urls")),
    path("edc_randomization/", include("edc_randomization.urls")),
    path("edc_consent/", include("edc_consent.urls")),
    path("edc_dashboard/", include("edc_dashboard.urls")),
    path("edc_export/", include("edc_export.urls")),
    path("edc_device/", include("edc_device.urls")),
    path("edc_protocol/", include("edc_protocol.urls")),
    path("edc_visit_schedule/", include("edc_visit_schedule.urls")),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]
