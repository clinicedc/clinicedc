from edc_navbar import Navbar, NavbarItem, site_navbars


navbar = Navbar(name='edc_export')

navbar.append_item(
    NavbarItem(name='export',
               label='Export',
               fa_icon='fas fa-file-export',
               url_name='edc_export:home_url'))

navbar.append_item(
    NavbarItem(name='data_request',
               label='Export Admin',
               # fa_icon='fas fa-file-export',
               url_name='edc_export:admin:index'))


site_navbars.register(navbar)
