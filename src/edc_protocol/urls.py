from django.conf.urls import url
from django.contrib import admin

from .views import HomeView

app_name = 'edc_protocol'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', HomeView.as_view(), name='home_url'),
]
