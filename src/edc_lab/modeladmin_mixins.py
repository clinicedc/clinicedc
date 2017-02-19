from django.contrib import admin

from .actions import (flag_as_received, flag_as_not_received,
                      flag_as_not_labelled, print_requisition_label)


class AliquotTypeModelAdminMixin(admin.ModelAdmin):

    list_display = ('name', 'alpha_code', 'numeric_code')


class AliquotProcessingModelAdminMixin:

    list_display = (
        'aliquot', 'profile', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('aliquot__aliquot_identifier', 'profile__profile_name', 'aliquot__aliquot_type__name',
                     'aliquot__aliquot_type__alpha_code', 'aliquot__aliquot_type__numeric_code')

    list_filter = (
        'profile', 'created', 'modified', 'user_created', 'user_modified')


class AliquotProfileModelAdminMixin(admin.ModelAdmin):

    list_display = (
        'name', 'aliquot_type', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('name', 'aliquot_type__name',
                     'aliquot_type__alpha_code', 'aliquot_type__numeric_code')

    list_filter = ('aliquot_type__name', 'aliquot_type__alpha_code',
                   'aliquot_type__numeric_code', 'created', 'modified', 'user_created', 'user_modified')


class AliquotProfileItemModelAdminMixin(admin.ModelAdmin):

    list_display = ('profile', 'aliquot_type', 'created',
                    'modified', 'user_created', 'user_modified')

    search_fields = ('profile__profile_name', 'aliquot_type__name',
                     'aliquot_type__alpha_code', 'aliquot_type__numeric_code')

    list_filter = ('aliquot_type__name', 'aliquot_type__alpha_code',
                   'aliquot_type__numeric_code', 'created', 'modified', 'user_created', 'user_modified')


class RequisitionAdminMixin:

    date_hierarchy = 'requisition_datetime'

    actions = [
        flag_as_received,
        flag_as_not_received,
        flag_as_not_labelled,
        print_requisition_label,
    ]

    radio_fields = {
        'is_drawn': admin.VERTICAL,
        'reason_not_drawn': admin.VERTICAL,
        'item_type': admin.VERTICAL,
    }

    list_display = [
        'requisition_identifier',
        'requisition_datetime',
        'panel_name',
        'hostname_created']

    list_filter = [
        'panel_name',
        'requisition_datetime',
        'study_site',
        'user_created',
        'hostname_created',
        'user_modified',
    ]

    search_fields = [
        'subject_identifier',
        'specimen_identifier',
        'requisition_identifier',
        'panel_name']
