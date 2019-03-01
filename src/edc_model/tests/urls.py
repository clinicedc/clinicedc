from django.conf import settings
from django.conf.urls import url
from django.contrib import admin

app_name = "edc_model"

urlpatterns = [url(r"^admin/", admin.site.urls)]


if settings.APP_NAME == app_name:
    from django.urls.conf import path

    from .admin import edc_model_admin

    urlpatterns += [path("admin/", edc_model_admin.urls)]
