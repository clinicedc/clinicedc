from django.conf import settings
from edc_navbar import Navbar, NavbarItem, site_navbars

device = Navbar(name='edc_device')

if settings.APP_NAME == 'edc_device':
    url_namespace = None
else:
    url_namespace = 'edc_device'

device.append_item(
    NavbarItem(name='device',
               label='device',
               fa_icon='fa-calculator',
               url_name=':'.join(x for x in [url_namespace, 'home_url'] if x)))

site_navbars.register(device)
