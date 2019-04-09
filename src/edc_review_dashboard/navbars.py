from edc_navbar import NavbarItem, site_navbars, Navbar


navbar = Navbar(name="edc_review_dashboard")

navbar.append_item(
    NavbarItem(
        name="subject_review",
        label="Review",
        codename="edc_dashboard.view_subject_review_listboard",
        url_name="subject_review_listboard_url",
    )
)

site_navbars.register(navbar)
