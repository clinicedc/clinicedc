from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_rx_admin

app_name = "edc_rx"

urlpatterns = [
    path("admin/", edc_rx_admin.urls),
    path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
]
