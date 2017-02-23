from django.conf.urls import url

from .admin_site import edc_appointment_admin
from .views import HomeView

app_name = 'edc_appointment'

urlpatterns = [
    url(r'^admin/', edc_appointment_admin.urls),
    url(r'^', HomeView.as_view(), name='home_url'),
]
