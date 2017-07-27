from django.conf.urls import url

from .admin_site import edc_metadata_admin
from .views import HomeView

app_name = 'edc_metadata'

urlpatterns = [
    url(r'^admin/', edc_metadata_admin.urls),
    url(r'', HomeView.as_view(), name='home_url'),
]
