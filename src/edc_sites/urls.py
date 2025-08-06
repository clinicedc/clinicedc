from django.urls import path
from django.views.generic import RedirectView

from .admin_site import edc_sites_admin

app_name = "edc_sites"

urlpatterns = [
    path("admin/", edc_sites_admin.urls),
    path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
]
