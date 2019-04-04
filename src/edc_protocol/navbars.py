from edc_navbar import Navbar, NavbarItem, site_navbars


protocol = Navbar(name="edc_protocol")

protocol.append_item(
    NavbarItem(
        name="protocol",
        title="Protocol",
        label="protocol",
        codename="edc_navbar.nav_edc_protocol",
        url_name="edc_protocol:home_url",
    )
)

site_navbars.register(protocol)
