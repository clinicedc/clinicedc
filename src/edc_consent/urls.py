from django.conf.urls import url

from .views import HomeView
from .admin_site import edc_consent_admin

urlpatterns = [
    url(r'^admin/', edc_consent_admin.urls),
    url(r'^', HomeView.as_view(), name='home_url'),
]
