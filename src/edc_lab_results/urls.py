from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import edc_lab_results_admin

app_name = "edc_lab_results"

urlpatterns = [
    path("admin/", edc_lab_results_admin.urls),
    path(
        "",
        RedirectView.as_view(url="/edc_lab_results/admin/"),
        name="home_url",
    ),
]
