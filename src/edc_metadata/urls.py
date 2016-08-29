from django.conf.urls import include, url
from edc_meta_data.admin import edc_meta_data_admin

urlpatterns = [
    url(r'^admin/', include(edc_meta_data_admin.urls)),
]
