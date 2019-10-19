from django.conf import settings
from edc_navbar import NavbarItem, site_navbars, Navbar


no_url_namespace = True if settings.APP_NAME == "edc_adverse_event" else False

navbar = Navbar(name="edc_adverse_event")

navbar.append_item(
    NavbarItem(
        name="ae",
        title="Adverse Events",
        fa_icon="fa-heartbeat",
        url_name=f"{settings.ADVERSE_EVENT_APP_LABEL}:home_url",
        codename="edc_navbar.nav_edc_adverse_event",
        no_url_namespace=no_url_namespace,
    )
)

site_navbars.register(navbar)
