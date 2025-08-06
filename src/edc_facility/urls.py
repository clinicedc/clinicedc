from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_facility_admin

app_name = "edc_facility"

urlpatterns = [
    path("admin/", edc_facility_admin.urls),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]
