from django.contrib.sites.shortcuts import get_current_site
from edc_model_admin.admin_site import EdcAdminSite


class AdminSite(EdcAdminSite):

    site_url = "/administration/"

    def each_context(self, request):
        context = super().each_context(request)
        context.update(global_site=get_current_site(request))
        label = "Edc Adverse Events"
        context.update(site_title=label, site_header=label, index_title=label)
        return context


edc_adverse_event_admin = AdminSite(name="edc_adverse_event_admin")
