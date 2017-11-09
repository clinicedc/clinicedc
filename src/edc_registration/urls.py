from django.views.generic.base import RedirectView
from django.urls.conf import path

from .admin_site import edc_registration_admin

app_name = 'edc_registration'

urlpatterns = [
    path('admin/edc_registration/', edc_registration_admin.urls),
    path('admin/', edc_registration_admin.urls),
    path('', RedirectView.as_view(url='admin/edc_registration/'), name='home_url'),
]
