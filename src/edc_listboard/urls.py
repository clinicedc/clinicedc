from django.urls.conf import path
from edc_dashboard.views import HomeView

app_name = "edc_listboard"

urlpatterns = [
    path("", HomeView.as_view(), name="home_url"),
]
