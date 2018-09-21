from django.urls.conf import re_path, path

from .admin_site import edc_export_admin
from .views import HomeView, ExportModelsView

app_name = 'edc_export'

urlpatterns = [
    path('admin/', edc_export_admin.urls),
    path('export/', ExportModelsView.as_view(),
         name='export_selected_models_url'),
    re_path('(?P<action>cancel|confirm)/', HomeView.as_view(),
            name='home_url'),
    path('', HomeView.as_view(), name='home_url'),
]
