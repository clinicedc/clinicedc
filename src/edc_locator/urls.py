from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "edc_locator"

urlpatterns = [
    path("", RedirectView.as_view(url="/edc_locator/admin/"), name="home_url"),
]
