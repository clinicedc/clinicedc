"""edc_label URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import re_path, include, path
from django.contrib import admin

from .views import HomeView, ChangePrinterView, PrintLabelView

app_name = 'edc_label'

urlpatterns = [
    re_path('printer/change/(?P<printer_type>\w+)/',
            ChangePrinterView.as_view(), name='change_session_printer'),
    re_path('print/label/(?P<printer_name>\w+)/(?P<label_template_name>)\w+/',
            PrintLabelView.as_view(), name='print_label'),
    path('print/label/', PrintLabelView.as_view(), name='print_label'),
    path('print_server/change/',
         ChangePrinterView.as_view(), name='change_session_print_server'),
    re_path(r'print/(?P<label_name>\w+)/'
            '(?P<copies>\d+)/(?P<app_label>\w+)/'
            '(?P<model_name>\w+)/'
            '(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?'
            '[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
            HomeView.as_view(), name='print-test-label'),
    re_path(r'print/(?P<label_name>\w+)/$',
            HomeView.as_view(), name='print-test-label'),
    path('', HomeView.as_view(), name='home_url'),
]

if settings.APP_NAME == 'edc_label':
    url_patterns = urlpatterns + [
        path('accounts/', include('edc_base.auth.urls')),
        path(r'admin/', admin.site.urls),
        path(r'edc_base/', include('edc_base.urls', namespace='edc-base')),
    ]
