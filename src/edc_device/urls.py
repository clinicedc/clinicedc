from django.urls.conf import path
from edc_device.views import HomeView
from edc_base.views import AdministrationView, LoginView, LogoutView
from django.conf import settings


app_name = 'edc_device'


if settings.APP_NAME == 'edc_device':
    urlpatterns = [
        path('administration/', AdministrationView.as_view(),
             name='administration_url'),
        path('login', LoginView.as_view(), name='login_url'),
        path('logout', LogoutView.as_view(
            pattern_name='login_url'), name='logout_url')]
else:
    urlpatterns = []

urlpatterns += [
    path(r'', HomeView.as_view(), name='home_url'),
]
