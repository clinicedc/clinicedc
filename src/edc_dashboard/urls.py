from django.conf import settings
from django.contrib import admin
from django.urls.conf import path
from .views import ListboardView

app_name = 'edc_dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
]


if settings.APP_NAME == 'edc_dashboard':

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
    ]
