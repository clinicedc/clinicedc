from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

app_name = 'edc_dashboard'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]


if settings.APP_NAME == 'edc_dashboard':

    from .tests import edc_dashboard_admin

    urlpatterns = [
        url(r'^admin/', edc_dashboard_admin.urls),
        #         url(r'^listboard/', include('edc_dashboard_admin.tests.urls',
        #                                     namespace='edc-model-wrapper')),
    ]
