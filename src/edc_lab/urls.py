from django.conf.urls import url, include

from .admin_site import edc_lab_admin

app_name = 'edc_lab'

urlpatterns = [
    url(r'^admin/', edc_lab_admin.urls),
    url(r'', include('edc_lab_dashboard.urls'))

]
