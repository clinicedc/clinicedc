from django.contrib import admin


class RequisitionAdminMixin:

    date_hierarchy = 'requisition_datetime'

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
