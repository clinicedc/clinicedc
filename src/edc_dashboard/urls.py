from django.conf import settings
from django.contrib import admin
from django.urls.conf import path, include

from .views import ListboardView, AdministrationView

app_name = 'edc_dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
]


if settings.APP_NAME == 'edc_dashboard':

    from django.views.generic.base import RedirectView

    from .url_config import UrlConfig
    from .tests.admin import edc_dashboard_admin

    subject_listboard_url_config = UrlConfig(
        url_name='listboard_url',
        view_class=ListboardView,
        label='subject_listboard',
        identifier_label='subject_identifier',
        identifier_pattern='/w+')

    urlpatterns += subject_listboard_url_config.listboard_urls + [
        path('admin/', edc_dashboard_admin.urls),
        path('', RedirectView.as_view(url='admin/'), name='home_url'),
        path('edc_auth/', include('edc_auth.urls')),
        path('edc_base/', include('edc_base.urls')),
        path('edc_consent/', include('edc_consent.urls')),
        path('edc_device/', include('edc_device.urls')),
        path('edc_protocol/', include('edc_protocol.urls')),
        path('edc_visit_schedule/', include('edc_visit_schedule.urls')),
        path('administration/', AdministrationView.as_view(),
             name='administration_url'),
    ]
