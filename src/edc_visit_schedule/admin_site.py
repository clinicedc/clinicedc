from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):
    site_title = "Edc Visit Schedule"
    site_header = "Edc Visit Schedule"
    index_title = "Edc Visit Schedule"
    # site_url = "/edc_visit_schedule/"


edc_visit_schedule_admin = AdminSite(name="edc_visit_schedule_admin")
