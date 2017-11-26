from django.conf import settings
from django.contrib import admin
from django.urls.conf import path

app_name = 'edc_dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
]


if settings.APP_NAME == 'edc_dashboard':

    from .tests.admin import edc_dashboard_admin

    urlpatterns += [
        path('admin/', edc_dashboard_admin.urls),
    ]
