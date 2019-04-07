from django.urls.conf import path

from .views import HomeView

app_name = "edc_protocol"

urlpatterns = [path("", HomeView.as_view(), name="home_url")]
