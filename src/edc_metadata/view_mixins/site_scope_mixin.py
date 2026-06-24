from __future__ import annotations

from edc_data_manager.auth_objects import DATA_MANAGER_ROLE
from edc_sites.site import sites


class SiteScopeViewMixin:
    """Resolve the site ids a user may act on in the review screens.

    Data managers may work across every site on their profile (including the
    current one); everyone else is limited to their current + view-only sites.
    """

    def allowed_site_ids(self) -> list[int]:
        if self.request.user.userprofile.roles.filter(name=DATA_MANAGER_ROLE).exists():
            site_ids = {s.id for s in self.request.user.userprofile.sites.all()}
            site_ids.add(self.request.site.id)
            return sorted(site_ids)
        return sites.get_site_ids_for_user(request=self.request)
