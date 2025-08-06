from django.urls.conf import path
from django.views.generic import RedirectView

from .admin_site import edc_crf_admin

app_name = "edc_crf"

urlpatterns = [
    path("admin/", edc_crf_admin.urls),
    path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
]
