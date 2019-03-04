from django.conf.urls import url

from .admin_site import edc_consent_admin
from .views import HomeView

app_name = "edc_consent"

urlpatterns = [
    url("admin/", edc_consent_admin.urls),
    url("", HomeView.as_view(), name="home_url"),
]
