from django.urls.conf import path
from django.views.generic import RedirectView

from .admin_site import edc_unblinding_admin

app_name = "edc_unblinding"

urlpatterns = [
    path("admin/", edc_unblinding_admin.urls),
    path("", RedirectView.as_view(url="/edc_unblinding/admin/"), name="home_url"),
]
