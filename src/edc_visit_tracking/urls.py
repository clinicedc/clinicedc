from django.contrib import admin
from django.conf.urls import include, url

app_name = 'edc_visit_schedule'

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]
