from django.conf.urls import include, url

from .admin import edc_appointment_admin
from .views import HomeView

urlpatterns = [
    url(r'^admin/', include(edc_appointment_admin.urls)),
    url(r'^', HomeView.as_view(), name='edc-appointment-home-url'),
]
