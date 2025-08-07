from django.contrib import admin

from edc_consent.modeladmin_mixins import ModelAdminConsentMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import demo_consent_admin
from ..models import SubjectConsent


@admin.register(SubjectConsent, site=demo_consent_admin)
class SubjectConsentAdmin(
    SiteModelAdminMixin,
    ModelAdminConsentMixin,
    ModelAdminSubjectDashboardMixin,
    SimpleHistoryAdmin,
):
    # form = SubjectConsentForm
    pass
