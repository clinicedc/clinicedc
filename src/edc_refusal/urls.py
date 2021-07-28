from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "edc_refusal"

urlpatterns = [
    path("", RedirectView.as_view(url="/edc_refusal/admin/"), name="home_url"),
]
