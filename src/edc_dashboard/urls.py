from django.conf.urls import url
from django.contrib import admin

app_name = 'edc_dasboard'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]
