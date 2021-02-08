from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):

    site_title = "EDC Pandas Utils"
    site_header = "EDC Pandas Utils"
    index_title = "EDC Pandas Utils"


edc_pdutils_admin = AdminSite(name="edc_pdutils_admin")
