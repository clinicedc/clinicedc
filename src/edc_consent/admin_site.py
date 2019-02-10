from django.contrib.admin.sites import AdminSite


class EdcConsentAdminSite(AdminSite):
    site_header = "Consent"
    site_title = "Consent"
    index_title = "Consent"
    site_url = "/edc_consent/"


edc_consent_admin = EdcConsentAdminSite(name="edc_consent_admin")
edc_consent_admin.disable_action("delete_selected")
