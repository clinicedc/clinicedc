from django.conf.urls import url

from edc_device.views import HomeView

app_name = 'edc_device'

urlpatterns = [
    url(r'^', HomeView.as_view(), name='home_url'),
]
