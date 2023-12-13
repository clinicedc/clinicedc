from ..single_site import SingleSite
from .sites import sites


class SiteTestCaseMixin:
    @classmethod
    def get_default_sites(cls) -> list[SingleSite]:
        return sites

    @property
    def default_sites(self) -> list[SingleSite]:
        return sites

    @property
    def site_names(self):
        return [s.name for s in self.default_sites]

    @staticmethod
    def sites_factory(language_codes) -> list[SingleSite]:
        return [
            SingleSite(
                10,
                "mochudi",
                title="Mochudi",
                country="botswana",
                country_code="bw",
                language_codes=language_codes,
                domain="mochudi.bw.clinicedc.org",
            ),
            SingleSite(
                20,
                "molepolole",
                title="Molepolole",
                country="botswana",
                country_code="bw",
                language_codes=language_codes,
                domain="molepolole.bw.clinicedc.org",
            ),
            SingleSite(
                30,
                "lobatse",
                title="Lobatse",
                country="botswana",
                country_code="bw",
                language_codes=language_codes,
                domain="lobatse.bw.clinicedc.org",
            ),
            SingleSite(
                40,
                "gaborone",
                title="Gaborone",
                country="botswana",
                country_code="bw",
                language_codes=language_codes,
                domain="gaborone.bw.clinicedc.org",
            ),
            SingleSite(
                50,
                "karakobis",
                title="Karakobis",
                country="botswana",
                country_code="bw",
                language_codes=language_codes,
                domain="karakobis.bw.clinicedc.org",
            ),
            SingleSite(
                60,
                "windhoek",
                title="Windhoek",
                country="namibia",
                country_code="na",
                language_codes=language_codes,
                domain="windhoek.bw.clinicedc.org",
            ),
        ]
