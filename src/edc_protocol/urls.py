from django.conf import settings
from django.contrib import admin
from django.urls.conf import path
from edc_base.views import AdministrationView, LoginView, LogoutView

from .views import HomeView

app_name = 'edc_protocol'

if settings.APP_NAME == 'edc_protocol':
    urlpatterns = [
        path('administration/', AdministrationView.as_view(),
             name='administration_url'),
        path('login', LoginView.as_view(), name='login_url'),
        path('logout', LogoutView.as_view(
            pattern_name='login_url'), name='logout_url')]
else:
    urlpatterns = []

urlpatterns += [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home_url'),
]
