from django.contrib import admin

from edc_consent.modeladmin_mixins import ModelAdminConsentMixin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from ..admin_site import demo_consent_admin
from ..models import SubjectConsentV1


@admin.register(SubjectConsentV1, site=demo_consent_admin)
class SubjectConsentV1Admin(
    SiteModelAdminMixin,
    ModelAdminConsentMixin,
    ModelAdminSubjectDashboardMixin,
    SimpleHistoryAdmin,
):
    # form = SubjectConsentForm
    pass
