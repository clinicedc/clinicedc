from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "demo_ae"

urlpatterns = [
    path("", RedirectView.as_view(url="/demo_ae/admin/"), name="home_url"),
]
