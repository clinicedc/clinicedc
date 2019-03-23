from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from .views import CrfOneListView

app_name = "edc_model_admin"

urlpatterns = [path("admin/", admin.site.urls)]

if settings.APP_NAME == app_name:
    urlpatterns += [
        path("", CrfOneListView.as_view(), name="crfone-list"),
        path("", include("edc_model_admin.tests.dashboard_app.urls")),
        path("", include("edc_model_admin.tests.dashboard2_app.urls")),
    ]
