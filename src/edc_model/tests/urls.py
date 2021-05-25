from django.urls import path

from .admin_site import edc_model_admin

app_name = "edc_model"

urlpatterns = [
    path("admin/", edc_model_admin.urls),
    path("", edc_model_admin.urls),
]
