from django.contrib import admin
from django.urls.conf import path

from .views import HomeView

app_name = "edc_dashboard"

urlpatterns = [path("admin/", admin.site.urls)]
urlpatterns = [path("", HomeView.as_view(), name="home_url")]
