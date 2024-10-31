from django.contrib import admin
from django_audit_fields import ModelAdminAuditFieldsMixin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    TemplatesModelAdminMixin,
)

from ...admin_site import meta_pharmacy_admin
from ...models import StockTransferItems


@admin.register(StockTransferItems, site=meta_pharmacy_admin)
class StockTransferItemsAdmin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,  # add
    ModelAdminFormInstructionsMixin,  # add
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,  # add
    ModelAdminInstitutionMixin,  # add
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminAuditFieldsMixin,
    admin.ModelAdmin,
):
    pass
