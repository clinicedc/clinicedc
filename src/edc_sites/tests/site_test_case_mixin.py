from ..single_site import SingleSite

fqdn = "clinicedc.org"


class SiteTestCaseMixin:
    @property
    def default_sites(self):
        return [
            SingleSite(
                10, "mochudi", "Mochudi", country="bw", domain=f"mochudi.bw.{fqdn}"
            ),
            SingleSite(20, "molepolole", "molepolole", fqdn=fqdn),
            SingleSite(30, "lobatse", "lobatse", fqdn=fqdn),
            SingleSite(40, "gaborone", "gaborone", fqdn=fqdn),
            SingleSite(50, "karakobis", "karakobis", fqdn=fqdn),
        ]

    @property
    def site_names(self):
        return [s.name for s in self.default_sites]
