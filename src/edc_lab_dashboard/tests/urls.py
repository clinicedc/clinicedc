from django.conf.urls import include
from django.urls.conf import path
from django.views.generic.base import TemplateView
from edc_lab.admin_site import edc_lab_admin

urlpatterns = [
    path("admin/", edc_lab_admin.urls),
    path("edc_dashboard/", include("edc_dashboard.urls")),
    path("edc_device/", include("edc_device.urls")),
    path("edc_label/", include("edc_label.urls")),
    path("edc_lab/", include("edc_lab.urls")),
    path("edc_protocol/", include("edc_protocol.urls")),
    path("edc_lab_dashboard/", include("edc_lab_dashboard.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="administration_url"),
    path("", TemplateView.as_view(template_name="home.html"), name="logout"),
    path("", TemplateView.as_view(template_name="home.html"), name="home_url"),
]
