from django.apps import apps as django_apps

from .navbar import Navbar
from .navbar_item import NavbarItem
from .site_navbars import site_navbars

app_config = django_apps.get_app_config('edc_navbar')

if app_config.register_default_navbar:

    default_navbar = Navbar(name=app_config.default_navbar_name)

    default_navbar.append_item(
        NavbarItem(name='home',
                   title='Home',
                   glyphicon='glyphicon-home',
                   url_name='home_url'))

    default_navbar.append_item(
        NavbarItem(name='administration',
                   title='Administration',
                   glyphicon='glyphicon-wrench',
                   url_name='administration_url'))

    default_navbar.append_item(
        NavbarItem(name='logout',
                   title='Logout',
                   glyphicon='glyphicon-log-out',
                   url_name='logout_url'))

    site_navbars.register(default_navbar)
