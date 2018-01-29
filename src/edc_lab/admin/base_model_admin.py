from django.contrib import admin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_fieldsets import FieldsetsModelAdminMixin
from edc_model_admin import (
    ModelAdminAuditFieldsMixin, ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin, ModelAdminFormAutoNumberMixin,
    ModelAdminReadOnlyMixin)


class BaseModelAdmin(ModelAdminFormInstructionsMixin,
                     ModelAdminNextUrlRedirectMixin,
                     ModelAdminFormAutoNumberMixin,
                     ModelAdminRevisionMixin,
                     ModelAdminAuditFieldsMixin,
                     ModelAdminReadOnlyMixin,
                     FieldsetsModelAdminMixin,
                     admin.ModelAdmin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'
    view_on_site = False
    show_cancel = True
