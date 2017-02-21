from django.contrib import admin

from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_base.fieldsets import FieldsetsModelAdminMixin, Fieldset
from edc_base.modeladmin_mixins import (
    audit_fieldset_tuple, audit_fields,
    ModelAdminAuditFieldsMixin, ModelAdminFormInstructionsMixin,
    ModelAdminNextUrlRedirectMixin, ModelAdminFormAutoNumberMixin,
    ModelAdminReadOnlyMixin)

from .admin_site import edc_lab_admin
from .forms import (
    BoxForm, BoxItemForm, SimpleBoxItemForm, BoxTypeForm, AliquotForm)
from .models import (
    Aliquot, Manifest, Destination, BoxItem, Box, SimpleBox, BoxType)


aliquot_identifiers_fields = (
    'subject_identifier',
    'requisition_identifier',
    'parent_identifier',
    'identifier_prefix')

aliquot_identifiers_fieldset_tuple = Fieldset(
    *aliquot_identifiers_fields,
    section='Identifiers').fieldset


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

    form = AliquotForm

    fieldsets = (
        (None, {
            'fields': (
                'aliquot_identifier',
                'aliquot_datetime',
                'aliquot_type',
                'condition',
            )}),
        aliquot_identifiers_fieldset_tuple,
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj)
                + audit_fields
                + aliquot_identifiers_fields)

    list_display = ('aliquot_identifier', 'subject_identifier',
                    'aliquot_datetime', 'aliquot_type', 'condition')

    list_filter = ('aliquot_datetime', 'aliquot_type', 'condition')

    search_fields = ('aliquot_identifier', 'subject_identifier', )

    radio_fields = {
        'condition': admin.VERTICAL}


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


@admin.register(Box, site=edc_lab_admin)
class BoxAdmin(BaseModelAdmin, admin.ModelAdmin):

    form = BoxForm

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'box_type',
                'specimen_types',
                'box_datetime',
                'category',
                'category_other',
                'comment')}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields

    list_display = (
        'box_identifier', 'name', 'category', 'specimen_types', 'box_type',
        'box_datetime', 'user_created', 'user_modified')


@admin.register(BoxItem, site=edc_lab_admin)
class BoxItemAdmin(BaseModelAdmin, admin.ModelAdmin):

    form = BoxItemForm

    fieldsets = (
        (None, {
            'fields': (
                'box',
                'position',
                'identifier',
                'comment')}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields

    list_display = ('identifier', 'position', )


@admin.register(BoxType, site=edc_lab_admin)
class BoxTypeAdmin(BaseModelAdmin, admin.ModelAdmin):

    form = BoxTypeForm

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'across',
                'down',
                'total',
                'fill_order',
            )}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields

    list_display = ('name', 'across', 'down', 'total')


class BoxItemInlineAdmin(admin.TabularInline):
    model = BoxItem
    form = SimpleBoxItemForm
    extra = 1


@admin.register(SimpleBox, site=edc_lab_admin)
class BoxAdmin2(BaseModelAdmin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',)}), )

    inlines = [BoxItemInlineAdmin]

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields
