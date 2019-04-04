from django.conf import settings
from edc_navbar import Navbar, NavbarItem, site_navbars

device = Navbar(name="edc_device")

no_url_namespace = True if settings.APP_NAME == "edc_device" else False

device.append_item(
    NavbarItem(
        name="device",
        label="device",
        fa_icon="fa-calculator",
        no_url_namespace=no_url_namespace,
        codename="edc_navbar.nav_edc_device",
        url_name="edc_device:home_url",
    )
)

site_navbars.register(device)
