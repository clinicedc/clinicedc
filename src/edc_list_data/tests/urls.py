from django.urls import path

from .admin import edc_list_data_admin

urlpatterns = [path("admin/", edc_list_data_admin.urls)]
