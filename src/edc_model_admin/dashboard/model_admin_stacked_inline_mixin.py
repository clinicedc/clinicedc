from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_notification import NotificationModelAdminMixin

from edc_model_admin import (
    ModelAdminAuditFieldsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    TemplatesModelAdminMixin,
)


class ModelAdminStackedInlineMixin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,
    NotificationModelAdminMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin,
):
    pass
