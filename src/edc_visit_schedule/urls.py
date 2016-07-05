from django.contrib import admin
from django.conf.urls import include, url
from edc_visit_schedule.admin import edc_visit_schedule_admin
from edc_visit_schedule.views import HomeView

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(edc_visit_schedule_admin.urls)),
    url(r'', HomeView.as_view(), name='edc-visit-schedule-home-url'),
]
