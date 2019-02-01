from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_notification_admin

app_name = "edc_notification"

urlpatterns = [
    path("admin/", edc_notification_admin.urls),
    path("", RedirectView.as_view(url="/edc_notification/admin/"), name="home_url"),
]
