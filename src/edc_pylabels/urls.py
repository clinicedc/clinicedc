from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

app_name = "edc_pylabels"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
]
