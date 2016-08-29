from django.conf.urls import include, url
from edc_metadata.admin import edc_metadata_admin

urlpatterns = [
    url(r'^admin/', include(edc_metadata_admin.urls)),
]
