from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_pharmacy_admin

app_name = "edc_pharmacy"

urlpatterns = [
    path("admin/", edc_pharmacy_admin.urls),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]
