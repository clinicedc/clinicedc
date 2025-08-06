from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import edc_registration_admin

app_name = "edc_registration"

urlpatterns = [
    path("admin/", edc_registration_admin.urls),
    path("", RedirectView.as_view(url="/edc_registration/admin/"), name="home_url"),
]
