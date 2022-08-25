from django.urls.conf import path
from django.views.generic.base import RedirectView
from edc_listboard.views import ListboardView
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

from ..url_config import UrlConfig
from ..views import AdministrationView
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


urlpatterns = subject_listboard_url_config.listboard_urls

for app_name in [
    "edc_dashboard",
    "edc_auth",
    "edc_adverse_event",
    "edc_randomization",
    "edc_consent",
    "edc_export",
    "edc_device",
    "edc_protocol",
    "edc_reference",
    "edc_visit_schedule",
]:
    for p in paths_for_urlpatterns(app_name):
        urlpatterns.append(p)

urlpatterns += [
    path("admin/", edc_dashboard_admin.urls),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
    path("", RedirectView.as_view(url="admin/"), name="logout"),
]
