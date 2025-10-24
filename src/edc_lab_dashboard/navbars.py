from copy import copy

from edc_navbar import Navbar, NavbarItem, site_navbars

specimens_navbar = NavbarItem(
    name="specimens",
    label="Specimens",
    title="Specimens",
    fa_icon="fa-flask",
    codename="edc_lab_dashboard.nav_lab_section",
    url_names_key="requisition_listboard_url",
)

_specimens_navbar = copy(specimens_navbar)
_specimens_navbar.active = True
_specimens_navbar.label = None

navbar = Navbar(name="specimens")

navbar.register(
    NavbarItem(
        name="requisition",
        label="Requisition",
        codename="edc_lab_dashboard.nav_lab_requisition",
        url_names_key="requisition_listboard_url",
    )
)

navbar.register(
    NavbarItem(
        name="receive",
        label="Receive",
        codename="edc_lab_dashboard.nav_lab_receive",
        url_names_key="receive_listboard_url",
    )
)

navbar.register(
    NavbarItem(
        name="process",
        label="Process",
        codename="edc_lab_dashboard.nav_lab_process",
        url_names_key="process_listboard_url",
    )
)

navbar.register(
    NavbarItem(
        name="pack",
        label="Pack",
        codename="edc_lab_dashboard.nav_lab_pack",
        url_names_key="pack_listboard_url",
    )
)

navbar.register(
    NavbarItem(
        name="manifest",
        label="Manifest",
        codename="edc_lab_dashboard.nav_lab_manifest",
        url_names_key="manifest_listboard_url",
    )
)

navbar.register(
    NavbarItem(
        name="aliquot",
        label="Aliquot",
        codename="edc_lab_dashboard.nav_lab_aliquot",
        url_names_key="aliquot_listboard_url",
    )
)

navbar.register(
    NavbarItem(
        name="result",
        label="Result",
        codename="edc_lab_dashboard.nav_lab_result",
        url_names_key="result_listboard_url",
    )
)

navbar.register(
    NavbarItem(
        name="specimens",
        title="Specimens",
        fa_icon="fa-flask",
        codename="edc_lab_dashboard.nav_lab_section",
        url_names_key="requisition_listboard_url",
        active=True,
    )
)

site_navbars.register(navbar)
