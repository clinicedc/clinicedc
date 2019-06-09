from edc_navbar import NavbarItem, site_navbars, Navbar


navbar = Navbar(name="edc_review_dashboard")

navbar_item = NavbarItem(
    name="subject_review",
    label="Review",
    title="Subject Review",
    codename="edc_dashboard.view_subject_review_listboard",
    url_name="subject_review_listboard_url",
)


navbar.append_item(navbar_item)

site_navbars.register(navbar)
