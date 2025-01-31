from django.contrib import admin
from django.urls import path

app_name = "edc_model_to_dataframe"

urlpatterns = [path("admin/", admin.site.urls)]
