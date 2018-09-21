from django.conf.urls import url
from django.contrib import admin

from .admin_site import edc_export_admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', edc_export_admin.urls),
]
