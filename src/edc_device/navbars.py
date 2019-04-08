from edc_navbar import Navbar, NavbarItem, site_navbars

device = Navbar(name="edc_device")

device.append_item(
    NavbarItem(
        name="device",
        label="device",
        fa_icon="fa-calculator",
        codename="edc_navbar.nav_edc_device",
        url_name="edc_device:home_url",
    )
)

site_navbars.register(device)
