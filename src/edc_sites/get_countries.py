from django.apps import apps as django_apps


def get_countries() -> list[str]:
    """Returns the countries"""
    site_model_cls = django_apps.get_model("sites.site")
    countries = set(s.siteprofile.country for s in site_model_cls.objects.all())
    return sorted(list(countries))
