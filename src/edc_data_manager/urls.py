from django.urls import path

from .admin_site import edc_data_manager_admin
from .views import HomeView

app_name = "edc_data_manager"

urlpatterns = [
    path("admin/", edc_data_manager_admin.urls),
    path("", HomeView.as_view(), name="home_url"),
]
