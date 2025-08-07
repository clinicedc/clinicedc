from django.apps import AppConfig as DjangoAppConfig
from django.contrib.admin.apps import AdminConfig as DjangoAdminConfig
from django.core.management.color import color_style

style = color_style()


class AdminConfig(DjangoAdminConfig):
    default_site = "demo_edc.admin.AdminSite"


class AppConfig(DjangoAppConfig):
    name = "demo_edc"
    verbose_name = "DEMO Edc"
