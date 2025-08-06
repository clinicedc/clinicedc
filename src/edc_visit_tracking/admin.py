from django.contrib import admin

from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from .admin_site import edc_visit_tracking_admin
from .modeladmin_mixins import VisitModelAdminMixin
from .models import SubjectVisit


@admin.register(SubjectVisit, site=edc_visit_tracking_admin)
class SubjectVisitAdmin(
    SiteModelAdminMixin,
    VisitModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    SimpleHistoryAdmin,
):
    pass
