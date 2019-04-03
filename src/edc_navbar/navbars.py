from django.apps import apps as django_apps

from .navbar import Navbar
from .navbar_item import NavbarItem
from .site_navbars import site_navbars

app_config = django_apps.get_app_config("edc_navbar")

if app_config.register_default_navbar:

    default_navbar = Navbar(name=app_config.default_navbar_name)

    default_navbar.append_item(
        NavbarItem(
            name="home",
            title="Home",
            fa_icon="fas fa-home",
            url_name="home_url",
            codename="edc_navbar.nav_home",
        )
    )

    default_navbar.append_item(
        NavbarItem(
            name="administration",
            title="Administration",
            fa_icon="fas fa-cog",
            codename="edc_navbar.nav_administration",
            url_name="administration_url",
        )
    )

    default_navbar.append_item(
        NavbarItem(
            name="logout",
            title="Logout",
            fa_icon="fas fa-sign-out-alt",
            url_name="logout",
            codename="edc_navbar.nav_logout",
        )
    )

    site_navbars.register(default_navbar)
