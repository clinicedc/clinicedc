from django.urls.conf import include, path
from django.views.generic.base import RedirectView
from edc_dashboard.views import AdministrationView
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

app_name = "edc_device"

urlpatterns = [
    path("accounts/", include("edc_auth.urls")),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    path("i18n/", include("django.conf.urls.i18n")),
    *paths_for_urlpatterns("edc_auth"),
    *paths_for_urlpatterns("edc_dashboard"),
    *paths_for_urlpatterns("edc_device"),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]
