from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_ltfu_admin

app_name = "edc_ltfu"

urlpatterns = [
    path("admin/", edc_ltfu_admin.urls),
    path("", RedirectView.as_view(url="/edc_ltfu/admin/"), name="home_url"),
]
