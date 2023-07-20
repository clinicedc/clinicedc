from django.contrib import admin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from .admin_site import edc_locator_admin
from .forms import SubjectLocatorForm
from .modeladmin_mixins import SubjectLocatorModelAdminMixin
from .models import SubjectLocator


@admin.register(SubjectLocator, site=edc_locator_admin)
class SubjectLocatorAdmin(
    SubjectLocatorModelAdminMixin,
    SiteModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    SimpleHistoryAdmin,
):
    form = SubjectLocatorForm
