from .navbar import Navbar
from .navbar_item import NavbarItem
from .site_navbars import site_navbars
from .utils import get_default_navbar_name, get_register_default_navbar

if get_register_default_navbar():
    default_navbar = Navbar(name=get_default_navbar_name())

    default_navbar.register(
        NavbarItem(
            name="home",
            title="Home",
            fa_icon="fa-home",
            url_without_namespace="home_url",
            codename="edc_navbar.nav_home",
        )
    )

    default_navbar.register(
        NavbarItem(
            name="administration",
            title="Administration",
            fa_icon="fa-cog",
            codename="edc_navbar.nav_administration",
            # url_names_key="administration",
            url_without_namespace="administration_url",
        )
    )

    site_navbars.register(default_navbar)
