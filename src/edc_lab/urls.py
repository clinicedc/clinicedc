from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import edc_lab_admin

app_name = "edc_lab"

urlpatterns = [
    path("admin/", edc_lab_admin.urls),
    path("", RedirectView.as_view(url="admin/edc_lab/"), name="home_url"),
]
