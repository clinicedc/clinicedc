from edc_navbar import Navbar, NavbarItem, site_navbars

navbar = Navbar(name="edc_consent")

navbar.append_item(
    NavbarItem(
        name="consent",
        label="Consent",
        fa_icon="far fa-user-circle",
        url_name="edc_consent:home_url",
        codename="edc_navbar.nav_consent",
    )
)

site_navbars.register(navbar)
