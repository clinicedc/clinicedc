from edc_navbar import Navbar, NavbarItem, site_navbars


consent = Navbar(name='edc_consent')

consent.append_item(
    NavbarItem(name='consent',
               label='Consent',
               fa_icon='fa-user-circle-o',
               url_name='edc_consent:home_url'))

site_navbars.register(consent)
