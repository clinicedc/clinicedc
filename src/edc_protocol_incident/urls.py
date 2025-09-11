from django.urls import path
from django.views.generic import RedirectView

app_name = "edc_protocol_incident"

urlpatterns = [
    path("", RedirectView.as_view(url="/edc_protocol_incident/admin/"), name="home_url"),
]
