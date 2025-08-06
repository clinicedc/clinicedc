from django.urls.conf import path

from edc_device.views import HomeView

app_name = "edc_device"

urlpatterns = [path("", HomeView.as_view(), name="home_url")]
