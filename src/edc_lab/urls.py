from django.urls.conf import path

from .admin_site import edc_lab_admin

app_name = 'edc_lab'

urlpatterns = [
    path('admin/', edc_lab_admin.urls),
]
