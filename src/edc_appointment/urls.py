from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from edc_base.views import LoginView, LogoutView

from .views import HomeView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', HomeView.as_view(), name='home_url'),
    url(r'^admin/$', RedirectView.as_view(pattern_name='home_url')),
    url(r'^', HomeView.as_view(), name='edc-appointment-home-url'),
    url(r'login', LoginView.as_view(), name='login_url'),
    url(r'logout', LogoutView.as_view(pattern_name='login_url'), name='logout_url'),
    url(r'^edc/', include('edc_base.urls')),
]
