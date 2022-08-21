from edc_navbar import Navbar, NavbarItem, site_navbars

navbar = Navbar(name="edc_export")

navbar.append_item(
    NavbarItem(
        name="export",
        label="Export",
        fa_icon="fa-solid fa-file-export",
        url_name="edc_export:home_url",
        codename="edc_navbar.nav_export",
    )
)

navbar.append_item(
    NavbarItem(
        name="data_request",
        label="Export Admin",
        # fa_icon='fas fa-file-export',
        url_name="edc_export:admin:index",
        codename="edc_navbar.nav_export",
    )
)


site_navbars.register(navbar)
