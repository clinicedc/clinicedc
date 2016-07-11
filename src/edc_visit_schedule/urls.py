from django.contrib import admin
from django.conf.urls import include, url
from edc_visit_schedule.views import HomeView

admin.autodiscover()

urlpatterns = [
    url(r'', HomeView.as_view(), name='edc-visit-schedule-home-url'),
]
