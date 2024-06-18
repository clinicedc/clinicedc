from django.urls import path
from django.views.generic import RedirectView

from .admin_site import edc_qareports_admin

app_name = "edc_qareports"

urlpatterns = [
    path("/admin/", edc_qareports_admin.urls),
    path("", RedirectView.as_view(url="/edc_qareports/admin/"), name="home_url"),
]
