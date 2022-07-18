from django.urls.conf import path
from edc_protocol.protocol import Protocol

from .admin_site import edc_adverse_event_admin
from .views import AeHomeView, ClosedTmgAeListboardView
from .views import DeathListboardView as TmgDeathListboardView
from .views import NewTmgAeListboardView, OpenTmgAeListboardView
from .views import SummaryListboardView as TmgSummaryListboardView
from .views import TmgHomeView

app_name = "edc_adverse_event"


urlpatterns = NewTmgAeListboardView.urls(
    namespace=app_name,
    label="new_tmg_ae_listboard",
    identifier_pattern=Protocol().subject_identifier_pattern,
)
urlpatterns += OpenTmgAeListboardView.urls(
    namespace=app_name,
    label="open_tmg_ae_listboard",
    identifier_pattern=Protocol().subject_identifier_pattern,
)
urlpatterns += ClosedTmgAeListboardView.urls(
    namespace=app_name,
    label="closed_tmg_ae_listboard",
    identifier_pattern=Protocol().subject_identifier_pattern,
)
urlpatterns += TmgDeathListboardView.urls(
    namespace=app_name,
    label="tmg_death_listboard",
    identifier_pattern=Protocol().subject_identifier_pattern,
)
urlpatterns += TmgSummaryListboardView.urls(
    namespace=app_name,
    label="tmg_summary_listboard",
    identifier_pattern=Protocol().subject_identifier_pattern,
)
urlpatterns += [
    path("tmg/", TmgHomeView.as_view(), name="tmg_home_url"),
    path("ae/", AeHomeView.as_view(), name="ae_home_url"),
    path("admin/", edc_adverse_event_admin.urls),
    path("", AeHomeView.as_view(), name="home_url"),
]
