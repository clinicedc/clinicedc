from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_metadata_admin
from .constants import REQUIRED

app_name = "edc_metadata"


class HomeRedirectView(RedirectView):
    """Land on the CrfMetadata changelist pre-filtered to REQUIRED.

    The administration section uses `edc_metadata:home_url` as the entry
    point for "Data Collection Status". Users almost always want to see
    outstanding (REQUIRED) records first; sending them to the admin
    index forced an extra click and an unfiltered scan. The filter can
    be cleared from the sidebar like any other admin filter.

    Defaults to CRF metadata. See also the `change_list_note` on the
    modeladmin classes.
    """

    permanent = False
    pattern_name = "edc_metadata_admin:edc_metadata_crfmetadata_changelist"

    def get_redirect_url(self, *args, **kwargs):
        url = super().get_redirect_url(*args, **kwargs)
        return f"{url}?entry_status__exact={REQUIRED}"


urlpatterns = [
    path("admin/", edc_metadata_admin.urls),
    path("", HomeRedirectView.as_view(), name="home_url"),
]
