from .navbar import Navbar
from .navbar_item import NavbarItem
from .site_navbars import site_navbars

default_navbar = Navbar(name='default')

default_navbar.append_item(
    NavbarItem(name='home',
               label='home',
               glyphicon='glyphicon-home',
               url_name='home_url'))

default_navbar.append_item(
    NavbarItem(name='administration',
               label='administration',
               glyphicon='glyphicon-wrench',
               url_name='administration_url'))

default_navbar.append_item(
    NavbarItem(name='logout',
               label='logout',
               glyphicon='glyphicon-log-out',
               url_name='logout_url'))

site_navbars.register(default_navbar)
