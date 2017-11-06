from django.urls import path

from .admin_site import edc_pharmacy_admin

app_name = 'edc_pharmacy'

urlpatterns = [
    path('admin/', edc_pharmacy_admin.urls),
]
