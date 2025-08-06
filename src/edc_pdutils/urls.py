from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_pdutils_admin

app_name = "edc_pdutils"

urlpatterns = [
    path("admin/", edc_pdutils_admin.urls),
    path("", RedirectView.as_view(url="/edc_pdutils/admin/"), name="home_url"),
]
