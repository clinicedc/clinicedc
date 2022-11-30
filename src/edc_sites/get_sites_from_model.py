import json

from django.apps import apps as django_apps

from .single_site import SingleSite


def get_sites_from_model() -> list[SingleSite]:
    sites = []
    site_model_cls = django_apps.get_model("edc_sites.edcsite")
    for obj in site_model_cls.objects.all():
        sites.append(
            SingleSite(
                obj.id,
                obj.name,
                title=obj.title,
                description=obj.description,
                country=obj.country,
                country_code=obj.country_code,
                domain=obj.domain,
                languages=json.loads(obj.languages) if obj.languages else None,
            )
        )
    return sites
