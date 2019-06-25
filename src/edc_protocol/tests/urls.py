from django.urls.conf import path, include
from edc_dashboard.views import AdministrationView

urlpatterns = [
    path("protocol/", include("edc_protocol.urls")),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
]
