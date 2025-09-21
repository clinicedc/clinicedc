from edc_auth.constants import PII, PII_VIEW
from edc_auth.site_auths import site_auths


def update_site_auths():
    site_auths.update_group(
        "edc_locator.add_subjectlocator",
        "edc_locator.change_subjectlocator",
        "edc_locator.view_historicalsubjectlocator",
        "edc_locator.view_subjectlocator",
        name=PII,
    )

    site_auths.update_group(
        "edc_locator.view_historicalsubjectlocator",
        "edc_locator.view_subjectlocator",
        name=PII_VIEW,
    )
    site_auths.add_pii_model("edc_locator.subjectlocator")


update_site_auths()
