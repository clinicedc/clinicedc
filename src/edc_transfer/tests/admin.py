from django.contrib import admin
from edc_model_admin import SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from edc_transfer.modeladmin_mixins import SubjectTransferModelAdminMixin

from .forms import SubjectTransferForm
from .models import SubjectTransfer


@admin.register(SubjectTransfer)
class SubjectTransferAdmin(
    SubjectTransferModelAdminMixin, ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin
):
    form = SubjectTransferForm
