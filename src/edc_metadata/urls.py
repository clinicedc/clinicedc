from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_metadata_admin

app_name = "edc_metadata"

urlpatterns = [
    path("admin/", edc_metadata_admin.urls),
    path("", RedirectView.as_view(url="/edc_metadata/admin/"), name="home_url"),
]
