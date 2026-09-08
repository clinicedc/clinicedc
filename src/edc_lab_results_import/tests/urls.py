from django.urls.conf import path
from django.views.generic import RedirectView

from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

urlpatterns = [
    *paths_for_urlpatterns("edc_lab_results_import"),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]
