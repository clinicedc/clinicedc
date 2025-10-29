from django.urls.conf import path

from edc_dashboard.url_names import url_names
from edc_protocol.research_protocol_config import ResearchProtocolConfig

from .admin_site import edc_adverse_event_admin
from .views import (
    AeHomeView,
    ClosedTmgAeListboardView,
    NewTmgAeListboardView,
    OpenTmgAeListboardView,
    TmgHomeView,
)
from .views import DeathListboardView as TmgDeathListboardView
from .views import SummaryListboardView as TmgSummaryListboardView

app_name = "edc_adverse_event"


urlpatterns = NewTmgAeListboardView.urls(
    namespace=app_name,
    url_names_key="new_tmg_ae_listboard_url",
    identifier_label="subject_identifier",
    identifier_pattern=ResearchProtocolConfig().subject_identifier_pattern,
)
urlpatterns += OpenTmgAeListboardView.urls(
    namespace=app_name,
    url_names_key="open_tmg_ae_listboard_url",
    identifier_label="subject_identifier",
    identifier_pattern=ResearchProtocolConfig().subject_identifier_pattern,
)
urlpatterns += ClosedTmgAeListboardView.urls(
    namespace=app_name,
    url_names_key="closed_tmg_ae_listboard_url",
    identifier_label="subject_identifier",
    identifier_pattern=ResearchProtocolConfig().subject_identifier_pattern,
)
urlpatterns += TmgDeathListboardView.urls(
    namespace=app_name,
    url_names_key="tmg_death_listboard_url",
    identifier_label="subject_identifier",
    identifier_pattern=ResearchProtocolConfig().subject_identifier_pattern,
)
urlpatterns += TmgSummaryListboardView.urls(
    namespace=app_name,
    url_names_key="tmg_summary_listboard_url",
    identifier_label="subject_identifier",
    identifier_pattern=ResearchProtocolConfig().subject_identifier_pattern,
)
urlpatterns += [
    path("tmg/", TmgHomeView.as_view(), name="tmg_home_url"),
    path("ae/", AeHomeView.as_view(), name="ae_home_url"),
    path("admin/", edc_adverse_event_admin.urls),
    path("", AeHomeView.as_view(), name="home_url"),
]

url_names.register(key="tmg_home_url", url_with_namespace=f"{app_name}:tmg_home_url")
url_names.register(key="ae_home_url", url_with_namespace=f"{app_name}:ae_home_url")
