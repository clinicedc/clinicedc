from django.urls.conf import include, path
from django.views.generic.base import RedirectView
from edc_dashboard.views import AdministrationView

urlpatterns = [
    path("accounts/", include("edc_auth.urls")),
    path("edc_dashboard/", include("edc_dashboard.urls")),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    path("edc_device/", include("edc_device.urls")),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]
