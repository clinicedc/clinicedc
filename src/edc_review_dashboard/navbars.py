from django.conf import settings
from edc_navbar import NavbarItem, site_navbars, Navbar


# no_url_namespace = True if settings.APP_NAME == "edc_review_dashboard" else False

navbar = Navbar(name="edc_review_dashboard")

navbar.append_item(
    NavbarItem(
        name="subject_review",
        label="Review",
        permission_codename="edc_dashboard.view_subject_review_listboard",
        url_name="subject_review_listboard_url",
    )
)

site_navbars.register(navbar)
