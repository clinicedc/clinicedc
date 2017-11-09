from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import edc_appointment_admin

app_name = 'edc_appointment'

urlpatterns = [
    path('admin/edc_appointment/', edc_appointment_admin.urls),
    path('admin/', edc_appointment_admin.urls),
    path('', RedirectView.as_view(url='admin/edc_appointment/'), name='home_url'),
]
