from django.urls.conf import path
from django.views.generic.base import RedirectView
from edc_dashboard import UrlConfig
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

from edc_listboard.views import ListboardView

from .admin import edc_listboard_admin

app_name = "edc_listboard"

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
    "edc_auth",
    "edc_listboard",
]:
    for p in paths_for_urlpatterns(app_name):
        urlpatterns.append(p)

urlpatterns += [
    path("admin/", edc_listboard_admin.urls),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
    path("", RedirectView.as_view(url="admin/"), name="logout"),
]
