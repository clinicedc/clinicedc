from edc_navbar import Navbar, NavbarItem, site_navbars

navbar = Navbar(name="edc_dashboard")
navbar.append_item(
    NavbarItem(
        name="edc_dashboard",
        label="Edc Dashboard",
        fa_icon="fa-cogs",
        codename="edc_navbar.nav_edc_dashboard",
        url_name="edc_dashboard:home_url",
    )
)


site_navbars.register(navbar)
