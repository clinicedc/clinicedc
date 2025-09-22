from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_prn_admin

app_name = "edc_prn"

urlpatterns = [
    path("admin/", edc_prn_admin.urls),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]
