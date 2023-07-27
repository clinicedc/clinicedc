from django.urls.conf import path
from django.views.generic import RedirectView
from edc_dashboard.views import AdministrationView
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

app_name = "edc_facility"


urlpatterns = []

for app_name in ["edc_facility", "edc_auth"]:
    for p in paths_for_urlpatterns(app_name):
        urlpatterns.append(p)

urlpatterns += [
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
    path("", RedirectView.as_view(url="admin/"), name="logout"),
]
