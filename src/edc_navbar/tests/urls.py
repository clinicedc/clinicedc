from django.urls import path, include
from django.views.generic.base import View

urlpatterns = [
    path(r"edc_navbar/", include("edc_navbar.urls")),
    path(r"edc_dashboard/", include("edc_dashboard.urls")),
    path(r"", View.as_view(), name="navbar_one_url"),
    path(r"", View.as_view(), name="navbar_two_url"),
    path(r"", View.as_view(), name="logout"),
    path(r"", View.as_view(), name="administration_url"),
    path(r"", View.as_view(), name="home_url"),
]
