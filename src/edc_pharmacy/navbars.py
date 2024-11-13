from edc_navbar import Navbar, NavbarItem, site_navbars

pharmacy_navbar_item = NavbarItem(
    name="pharmacy",
    label="",
    title="",
    fa_icon="fa-prescription",
    codename="edc_pharmacy.nav_pharmacy_section",
    url_name="edc_pharmacy:home_url",
)

navbar = Navbar(name="pharmacy")

navbar.register(pharmacy_navbar_item)
site_navbars.register(navbar)
