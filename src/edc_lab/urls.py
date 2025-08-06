from django.urls.conf import path
from django.views.generic.base import RedirectView

app_name = "edc_lab"

urlpatterns = [
    path("", RedirectView.as_view(url="/edc_lab/admin/"), name="home_url"),
]
