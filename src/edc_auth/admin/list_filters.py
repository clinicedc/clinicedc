from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site


class SitesListFilter(SimpleListFilter):
    title = "Site"
    parameter_name = "site_name"

    def lookups(self, request, model_admin):  # noqa: ARG002
        sites = [
            (site.name, site.name.replace("_", " ").title())
            for site in Site.objects.all().order_by("name")
        ]
        return tuple(sites)

    def queryset(self, request, queryset):  # noqa: ARG002
        """Returns a queryset if the site name is in the list of sites"""
        qs = None
        if self.value():
            qs = get_user_model().objects.filter(userprofile__sites__name__in=[self.value()])
        return qs


class CountriesListFilter(SimpleListFilter):
    title = "Country"
    parameter_name = "country_name"

    def lookups(self, request, model_admin):  # noqa: ARG002
        countries = set(s.siteprofile.country for s in Site.objects.all())
        return tuple((c, c.replace("_", " ").title()) for c in sorted(countries))

    def queryset(self, request, queryset):  # noqa: ARG002
        """Returns a queryset if the country name is in a site's siteprofile,
        in the list of sites.
        """
        qs = None
        if self.value():
            qs = (
                get_user_model()
                .objects.filter(userprofile__sites__siteprofile__country__in=[self.value()])
                .distinct()
            )
        return qs
