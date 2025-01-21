from django.contrib import admin
from edc_lab.admin import RequisitionAdminMixin
from edc_model.models import BaseUuidModel

from .models import SubjectRequisition


@admin.register(SubjectRequisition)
class SubjectRequisitionAdmin(RequisitionAdminMixin, BaseUuidModel):
    pass
