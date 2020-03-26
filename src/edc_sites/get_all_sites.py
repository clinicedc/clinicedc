from .get_sites_module import get_sites_module


def get_all_sites(name=None):
    all_sites = getattr(get_sites_module(), name or "all_sites")
    return all_sites
