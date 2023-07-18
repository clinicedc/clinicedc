from django.contrib.sites.models import Site


def get_countries() -> list[str]:
    """Returns the countries"""
    countries = set(s.siteprofile.country for s in Site.objects.all())
    return sorted(list(countries))
