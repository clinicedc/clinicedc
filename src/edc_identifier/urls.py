from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import edc_identifier_admin

app_name = "edc_identifier"

urlpatterns = [
    path("admin/", edc_identifier_admin.urls),
    path("", RedirectView.as_view(url="/edc_identifier/admin/"), name="home_url"),
]
