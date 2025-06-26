from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import edc_reportable_admin

app_name = "edc_reportable"

urlpatterns = [
    path("admin/", edc_reportable_admin.urls),
    path("", RedirectView.as_view(url="/edc_reportable/admin/"), name="home_url"),
]
