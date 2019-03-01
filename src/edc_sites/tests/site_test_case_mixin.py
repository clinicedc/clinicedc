from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist

fqdn = "clinicedc.org"

default_sites = [
    (10, "mochudi", "mochudi"),
    (20, "molepolole", "molepolole"),
    (30, "lobatse", "lobatse"),
    (40, "gaborone", "gaborone"),
    (50, "karakobis", "karakobis"),
]


class SiteTestCaseMixin:

    fqdn = fqdn

    default_sites = default_sites

    @property
    def site_names(self):
        return [s[1] for s in self.default_sites]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Site.objects.all().delete()
        for site_id, site_name, _ in cls.default_sites:
            try:
                Site.objects.get(pk=site_id)
            except ObjectDoesNotExist:
                Site.objects.create(
                    pk=site_id, name=site_name, domain=f"{site_name}.{cls.fqdn}"
                )
