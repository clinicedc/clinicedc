navbars = [
    "edc_navbar.nav_administration",
    "edc_navbar.nav_home",
    "edc_navbar.nav_export_section",
    "edc_navbar.nav_logout",
    "edc_navbar.nav_pharmacy_section",
    "edc_navbar.nav_public",
    "edc_navbar.nav_enrolment_section",
    "edc_navbar.nav_subject_section",
]

custom_codename_tuples = []
for codename in navbars:
    custom_codename_tuples.append((codename, f"Can access {codename.split('.')[1]}"))
