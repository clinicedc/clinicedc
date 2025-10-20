from edc_navbar import Navbar, NavbarItem, site_navbars

ae_navbar_item = NavbarItem(
    name="ae_home",
    title="Adverse Events",
    label="AE",
    codename="edc_adverse_event.nav_ae_section",
    url_names_key="ae_home_url",
    url_with_namespace="edc_adverse_event:ae_home_url",
)

tmg_navbar_item = NavbarItem(
    name="tmg_home",
    label="TMG",
    codename="edc_adverse_event.nav_tmg_section",
    url_names_key="tmg_home_url",
    url_with_namespace="edc_adverse_event:tmg_home_url",
)

ae_navbar = Navbar(name="edc_adverse_event")
ae_navbar.register(ae_navbar_item)
ae_navbar.register(tmg_navbar_item)

site_navbars.register(ae_navbar)
