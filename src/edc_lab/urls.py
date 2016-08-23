from django.conf.urls import url

from .admin_site import edc_lab_admin
from .views import HomeView

urlpatterns = [
    url(r'^admin/', edc_lab_admin.urls),
    url(r'^', HomeView.as_view(), name='home_url'),
]
