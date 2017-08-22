from django.conf.urls import url

from .admin_site import edc_identifier_admin
from .views import HomeView

app_name = 'edc_identifier'

urlpatterns = [
    url(r'^admin/', edc_identifier_admin.urls),
    url(r'', HomeView.as_view(), name='home_url'),
]
