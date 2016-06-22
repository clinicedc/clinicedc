from django.contrib import admin
from django.conf.urls import include, url

# from edc_base.utils import edc_base_startup

# edc_base_startup()
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]
