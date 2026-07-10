from django.urls.conf import path

from .admin_site import edc_lab_results_import_admin
from .views import HomeView

app_name = "edc_lab_results_import"

urlpatterns = [
    path("admin/", edc_lab_results_import_admin.urls),
    path(
        "",
        HomeView.as_view(),
        name="home_url",
    ),
]
