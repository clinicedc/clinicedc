from django.urls import path
from django.views.generic.base import View
from django.conf import settings


if settings.APP_NAME == 'edc_navbar':

    app_name = 'edc_navbar'
    urlpatterns = [
        path(r'one/', View.as_view(), name='navbar_one_url'),
        path(r'two/', View.as_view(), name='navbar_two_url'),
    ]
