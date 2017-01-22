from django.conf.urls import url

from .admin_site import edc_registration_admin


urlpatterns = [
    url(r'^admin/', edc_registration_admin.urls),
]
