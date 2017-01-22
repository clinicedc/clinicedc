from django.contrib import admin
from django.conf.urls import url
from edc_visit_schedule.views import HomeView

admin.autodiscover()

urlpatterns = [

    url(r'(?P<visit_schedule>[0-9A-Za-z_]+)/(?P<schedule>^[0-9A-Za-z_]+$)/(?P<visit_code>^[0-9]+$)/',
        HomeView.as_view(), name='home_url'),
    url(r'(?P<visit_schedule>[0-9A-Za-z_]+)/(?P<schedule>^[0-9A-Za-z_]+$)/',
        HomeView.as_view(), name='home_url'),
    url(r'(?P<visit_schedule>[0-9A-Za-z_]+)/',
        HomeView.as_view(), name='home_url'),
    url(r'', HomeView.as_view(), name='home_url'),
]
