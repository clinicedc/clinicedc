from django.contrib import admin
from django.urls.conf import path
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
]


if settings.APP_NAME == 'edc_subject_dashboard':

    from edc_appointment.admin_site import edc_appointment_admin
    from edc_subject_dashboard.tests.admin import edc_subject_dashboard_admin
    urlpatterns += [
        path('admin/', edc_subject_dashboard_admin.urls),
        path('admin/', edc_appointment_admin.urls),
    ]
