from django.urls import path
from django.contrib import admin
from django.views.generic.base import RedirectView

app_name = "edc_facility"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
]
