from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "demo_consent"

urlpatterns = [
    path("", RedirectView.as_view(url="/demo_consent/admin/"), name="home_url"),
]
