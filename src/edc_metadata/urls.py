from django.conf.urls import url

from .admin_site import edc_metadata_admin

app_name = 'edc_metadata'

urlpatterns = [
    url(r'^admin/', edc_metadata_admin.urls),
]
