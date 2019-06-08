from django.urls import path

from .admin_site import edc_data_manager_admin

app_name = "edc_data_manager"

urlpatterns = [
    path("admin/", edc_data_manager_admin.urls),
]
