from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_action_item_admin

app_name = 'edc_action_item'

urlpatterns = [
    path('admin/', edc_action_item_admin.urls),
    path('', RedirectView.as_view(url='/edc_action_item/admin/'), name='home_url'),
]
