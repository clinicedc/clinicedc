from django.contrib import admin
from django.urls import path
from edc_data_manager.views import HomeView

app_name = "edc_review_dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home_url"),
]
