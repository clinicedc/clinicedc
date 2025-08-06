from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "edc_ltfu"

urlpatterns = [
    path("", RedirectView.as_view(url="/edc_ltfu_admin/"), name="home_url"),
]
