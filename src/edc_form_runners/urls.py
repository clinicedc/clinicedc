from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "edc_form_runners"

urlpatterns = [
    path("", RedirectView.as_view(url="/edc_form_runners/admin/"), name="home_url"),
]
