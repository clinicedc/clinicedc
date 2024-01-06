from django.contrib.admin import SimpleListFilter
from django.contrib.sites.models import Site

from ..site import sites


class SiteListFilter(SimpleListFilter):
    title = "Site"
    parameter_name = "site"

    def lookups(self, request, model_admin):
        names = []
        site_ids = sites.get_site_ids_for_user(request=request)
        for site in Site.objects.filter(id__in=site_ids).order_by("id"):
            names.append((site.id, f"{site.id} {sites.get(site.id).description}"))
        return tuple(names)

    def queryset(self, request, queryset):
        if self.value() and self.value() != "none":
            queryset = queryset.filter(site__id=self.value())
        return queryset
