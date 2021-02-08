from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import edc_randomization_admin

app_name = "edc_randomization"

urlpatterns = [
    path("admin/", edc_randomization_admin.urls),
    path("", RedirectView.as_view(url="/edc_randomization/admin/"), name="home_url"),
]
