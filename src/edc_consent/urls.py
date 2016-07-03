from django.contrib import admin
from django.conf.urls import include, url

from edc_consent.views import HomeView
from edc_consent.admin import edc_consent_admin

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(edc_consent_admin.urls)),
    url(r'^', HomeView.as_view(), name='edc-consent-home-url'),
]
