from edc_navbar import Navbar, NavbarItem, site_navbars

navbar = Navbar(name="edc_visit_schedule")

navbar.register(
    NavbarItem(
        name="visit_schedule",
        title="Visit Schedule",
        label="Visit Schedule",
        fa_icon="fa-calendar",
        url_name="edc_visit_schedule:home_url",
        codename="edc_navbar.nav_visit_schedule",
    )
)

navbar.register(
    NavbarItem(
        name="admin",
        title="Subject History",
        label="Subject History",
        fa_icon="fa-history",
        url_name=(
            "edc_visit_schedule:edc_visit_schedule_admin:"
            "edc_visit_schedule_subjectschedulehistory_changelist"
        ),
        codename="edc_navbar.nav_visit_schedule",
    )
)

site_navbars.register(navbar)
