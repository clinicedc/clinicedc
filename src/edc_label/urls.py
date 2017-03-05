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
from django.conf.urls import url, include
from django.contrib import admin

from edc_base.views import LoginView, LogoutView

from edc_label.views import HomeView

app_name = 'edc_label'

urlpatterns = [
    url(r'login', LoginView.as_view(), name='login_url'),
    url(r'logout', LogoutView.as_view(
        pattern_name='login_url'), name='logout_url'),
    url(r'^print/(?P<label_name>\w+)/'
        '(?P<copies>\d+)/(?P<app_label>\w+)/'
        '(?P<model_name>\w+)/'
        '(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        HomeView.as_view(
        ), name='print-test-label'),
    url(r'^print/(?P<label_name>\w+)/$',
        HomeView.as_view(), name='print-test-label'),
    url(r'^edc_base/', include('edc_base.urls', namespace='edc-base')),
    url(r'^admin/', admin.site.urls),
    url(r'^', HomeView.as_view(), name='home_url'),
]
