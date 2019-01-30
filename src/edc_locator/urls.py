from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_locator_admin

app_name = "edc_locator"

urlpatterns = [
    path("admin/", edc_locator_admin.urls),
    path("", RedirectView.as_view(url="/edc_locator/admin/"), name="home_url"),
]
