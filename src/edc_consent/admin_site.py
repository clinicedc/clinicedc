from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_header = "Consent"
    site_title = "Consent"
    index_title = "Consent"
    site_url = "/edc_consent/"


edc_consent_admin = AdminSite(name="edc_consent_admin")
