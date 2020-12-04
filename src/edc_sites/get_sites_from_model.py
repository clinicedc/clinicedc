from django.apps import apps as django_apps

from .single_site import SingleSite


def get_sites_from_model():
    site_model_cls = django_apps.get_model("edc_sites.edcsite")
    return [
        SingleSite(
            obj.id,
            obj.name,
            title=obj.title,
            description=obj.description,
            country=obj.country,
            country_code=obj.country_code,
            domain=obj.domain,
        )
        for obj in site_model_cls.objects.all()
    ]
