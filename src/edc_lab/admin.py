from django.contrib import admin

from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_base.fieldsets import FieldsetsModelAdminMixin
from edc_base.modeladmin_mixins import (
    audit_fieldset_tuple, audit_fields,
    ModelAdminAuditFieldsMixin, ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin, ModelAdminFormAutoNumberMixin,
    ModelAdminReadOnlyMixin)

from .admin_site import edc_lab_admin
from .models import Aliquot, Manifest, Destination


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


@admin.register(Aliquot, site=edc_lab_admin)
class AliquotAdmin(BaseModelAdmin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'aliquot_identifier',
                'aliquot_datetime',
            )}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields

    list_display = ('aliquot_identifier', 'subject_identifier',
                    'aliquot_datetime', 'aliquot_type',)

    list_filter = ('aliquot_datetime', 'aliquot_type',)

    search_fields = ('aliquot_identifier', 'subject_identifier', )


class AliquotInlineAdmin(admin.TabularInline):
    model = Aliquot
    extra = 0
    fields = ('aliquot_identifier', )


@admin.register(Destination, site=edc_lab_admin)
class DestinationAdmin(BaseModelAdmin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'address',
                'tel',
                'email')}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields


@admin.register(Manifest, site=edc_lab_admin)
class ManifestAdmin(BaseModelAdmin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'manifest_identifier',
                'manifest_datetime',
            )}),
        audit_fieldset_tuple)

    inlines = [AliquotInlineAdmin]

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields

    list_display = ('manifest_identifier', 'manifest_datetime', )

    list_filter = ('manifest_datetime', )

    search_fields = ('manifest_identifier', )
