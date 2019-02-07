from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = "Edc Visit Schedule"
    site_header = "Edc Visit Schedule"
    index_title = "Edc Visit Schedule"
    site_url = "/edc_visit_schedule/"


edc_visit_schedule_admin = AdminSite(name="edc_visit_schedule_admin")
edc_visit_schedule_admin.disable_action("delete_selected")
