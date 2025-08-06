from django.urls.conf import path
from django.views.generic import RedirectView

from .admin_site import edc_auth_admin

app_name = "edc_auth"


urlpatterns = [
    path("admin/", edc_auth_admin.urls),
    path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
]
