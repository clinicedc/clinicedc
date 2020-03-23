from ..single_site import SingleSite

fqdn = "clinicedc.org"


class SiteTestCaseMixin:
    @property
    def default_sites(self):
        return [
            SingleSite(
                10,
                "mochudi",
                "Mochudi",
                country="botswana",
                country_code="bw",
                domain=f"mochudi.bw.{fqdn}",
            ),
            SingleSite(
                20,
                "molepolole",
                "molepolole",
                country="botswana",
                country_code="bw",
                fqdn=fqdn,
            ),
            SingleSite(
                30,
                "lobatse",
                "lobatse",
                country="botswana",
                country_code="bw",
                fqdn=fqdn,
            ),
            SingleSite(
                40,
                "gaborone",
                "gaborone",
                country="botswana",
                country_code="bw",
                fqdn=fqdn,
            ),
            SingleSite(
                50,
                "karakobis",
                "karakobis",
                country="botswana",
                country_code="bw",
                fqdn=fqdn,
            ),
            SingleSite(
                60,
                "windhoek",
                "windhoek",
                country="namibia",
                country_code="na",
                fqdn=fqdn,
            ),
        ]

    @property
    def site_names(self):
        return [s.name for s in self.default_sites]
