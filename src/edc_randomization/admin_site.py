from django.contrib.admin import AdminSite as DjangoAdminSite
from django.contrib.sites.shortcuts import get_current_site


class AdminSite(DjangoAdminSite):

    site_url = "/administration/"

    def each_context(self, request):
        context = super().each_context(request)
        context.update(global_site=get_current_site(request))
        label = "Randomization"
        context.update(site_title=label, site_header=label, index_title=label)
        return context


edc_randomization_admin = AdminSite(name="edc_randomization_admin")
edc_randomization_admin.disable_action("delete_selected")
