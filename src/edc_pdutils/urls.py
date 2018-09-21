from django.urls import path, re_path

from .admin_site import edc_pdutils_admin
from .views import HomeView, ExportModelsView

app_name = 'edc_pdutils'

urlpatterns = [
    path('admin/', edc_pdutils_admin.urls),
    path('export/', ExportModelsView.as_view(),
         name='export_selected_models_url'),
    re_path('(?P<action>cancel|confirm)/', HomeView.as_view(),
            name='home_url'),
    path('', HomeView.as_view(), name='home_url'),
]
