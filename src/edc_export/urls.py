from django.urls.conf import re_path, path

from .admin_site import edc_export_admin
from .views import HomeView, ExportModelsView, ExportSelectedModelsView

app_name = "edc_export"

urlpatterns = [
    path("admin/", edc_export_admin.urls),
    path(
        "selected_models/",
        ExportSelectedModelsView.as_view(),
        name="export_selected_models_url",
    ),
    re_path(
        "models/(?P<action>cancel|confirm)/",
        ExportModelsView.as_view(),
        name="export_models_url",
    ),
    re_path("models/", ExportModelsView.as_view(), name="export_models_url"),
    path("", HomeView.as_view(), name="home_url"),
]
