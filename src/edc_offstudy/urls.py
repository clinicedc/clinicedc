from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_offstudy_admin

app_name = "edc_offstudy"

urlpatterns = [
    path("admin/", edc_offstudy_admin.urls),
    path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
]
