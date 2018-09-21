from edc_navbar import Navbar, NavbarItem, site_navbars


navbar = Navbar(name='edc_pdutils')

navbar.append_item(
    NavbarItem(name='export',
               label='Export',
               fa_icon='fas fa-file-export',
               url_name='edc_pdutils:home_url'))

site_navbars.register(navbar)
