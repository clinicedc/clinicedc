from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site


class SitesListFilter(SimpleListFilter):

    title = "Site"
    parameter_name = "site_name"

    def lookups(self, request, model_admin):
        sites = []
        for site in Site.objects.all().order_by("name"):
            sites.append((site.name, site.name.replace("_", " ").title()))
        return tuple(sites)

    def queryset(self, request, queryset):
        """Returns a queryset if the site name is in the list of sites"""
        qs = None
        if self.value():
            qs = get_user_model().objects.filter(userprofile__sites__name__in=[self.value()])
        return qs
