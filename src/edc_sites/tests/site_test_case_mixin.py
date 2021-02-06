from .sites import all_sites, sites


class SiteTestCaseMixin:
    @property
    def default_sites(self):
        return sites

    @property
    def site_names(self):
        return [s.name for s in self.default_sites]

    @property
    def default_all_sites(self):
        return all_sites
