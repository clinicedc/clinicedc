from django.conf.urls import url

from .admin_site import edc_registration_admin
from django.views.generic.base import RedirectView

app_name = 'edc_registration'

urlpatterns = [
    url(r'^admin/', edc_registration_admin.urls),
    url(r'', RedirectView.as_view(url='/'), name='home_url'),
]
