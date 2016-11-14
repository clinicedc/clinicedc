from django.conf.urls import include, url

from .views import HomeView
from .admin_site import edc_consent_admin

urlpatterns = [
    url(r'^admin/', include(edc_consent_admin.urls)),
    url(r'^', HomeView.as_view(), name='home-url'),
]
