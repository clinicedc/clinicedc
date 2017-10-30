from django.contrib import admin
from django.conf.urls import url

app_name = 'edc_visit_schedule'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]
