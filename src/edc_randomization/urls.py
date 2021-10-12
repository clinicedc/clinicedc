from django.urls.conf import path
from django.views.generic.base import RedirectView

app_name = "edc_randomization"


urlpatterns = [
    path("", RedirectView.as_view(url="/edc_randomization/admin/"), name="home_url"),
]
