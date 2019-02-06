from edc_navbar import Navbar, NavbarItem, site_navbars


visit_schedule = Navbar(name="edc_visit_schedule")

visit_schedule.append_item(
    NavbarItem(
        name="visit_schedule",
        title="Visit Schedule",
        label="Visit Schedule",
        fa_icon="fa-calendar",
        url_name="edc_visit_schedule:home_url",
        permission_codename="edc_navbar.nav_visit_schedule",
    )
)

visit_schedule.append_item(
    NavbarItem(
        name="admin",
        title="Subject History",
        label="Subject History",
        fa_icon="fa-history",
        url_name=(
            "edc_visit_schedule:edc_visit_schedule_admin:"
            "edc_visit_schedule_subjectschedulehistory_changelist"
        ),
        permission_codename="edc_navbar.nav_visit_schedule",
    )
)

site_navbars.register(visit_schedule)
