from django.conf.urls import url

from .admin_site import edc_registration_admin

app_name = 'edc_registration'

urlpatterns = [
    url(r'^admin/', edc_registration_admin.urls),
]
