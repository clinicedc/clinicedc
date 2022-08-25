from django.conf import settings
from edc_navbar import Navbar, NavbarItem, site_navbars

no_url_namespace = True if settings.APP_NAME == "edc_adverse_event" else False

ae_navbar_item = NavbarItem(
    name="ae_home",
    title="Adverse Events",
    label="AE",
    codename="edc_adverse_event.nav_ae_section",
    url_name="edc_adverse_event:ae_home_url",
    no_url_namespace=no_url_namespace,
)

tmg_navbar_item = NavbarItem(
    name="tmg_home",
    label="TMG",
    codename="edc_adverse_event.nav_tmg_section",
    url_name="edc_adverse_event:tmg_home_url",
    no_url_namespace=no_url_namespace,
)

ae_navbar = Navbar(name="edc_adverse_event")
ae_navbar.append_item(ae_navbar_item)
ae_navbar.append_item(tmg_navbar_item)

site_navbars.register(ae_navbar)
