from edc_navbar import Navbar, NavbarItem, site_navbars

navbar = Navbar(name="edc_consent")

navbar.register(
    NavbarItem(
        name="consent",
        label="Consent",
        fa_icon="fa-user-circle",
        url_names_key="consent_home",
        url_with_namespace="edc_consent:home_url",
        codename="edc_consent.nav_consent",
    )
)

site_navbars.register(navbar)
