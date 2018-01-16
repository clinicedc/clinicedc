from django.conf import settings
from django.urls.conf import path
from edc_base.views import AdministrationView

from .views import HomeView

app_name = 'edc_protocol'

urlpatterns = [
    path('', HomeView.as_view(), name='home_url'),
]


if settings.APP_NAME == 'edc_protocol':
    urlpatterns = [
        path('administration/', AdministrationView.as_view(),
             name='administration_url')] + urlpatterns
