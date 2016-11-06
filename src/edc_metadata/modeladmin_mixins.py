
class CrfMetaDataAdminMixin:

    search_fields = (
        'subject_identifier', 'model', 'id')
    list_display = (
        'subject_identifier', 'model', 'visit_code', 'entry_status', 'fill_datetime',
        'due_datetime', 'close_datetime', 'created', 'hostname_created')
    list_filter = (
        'entry_status', 'visit_code', 'schedule_name', 'visit_schedule_name', 'model', 'fill_datetime',
        'created', 'user_created', 'hostname_created')
    readonly_fields = ('subject_identifier', 'model', 'visit_code', 'schedule_name', 'visit_schedule_name',
                       'show_order', 'current_entry_title')


# class RequisitionMetaDataAdminMixin:
#
#     search_fields = (
#         'registered_subject__subject_identifier', 'lab_entry__visit_definition__code',
#         'lab_entry__requisition_panel__name', 'id')
#     list_display = (
#         'registered_subject', 'lab_entry', 'entry_status', 'fill_datetime', 'due_datetime', 'close_datetime')
#     list_filter = (
#         'entry_status', 'lab_entry__visit_definition__code', 'fill_datetime',
#         'created', 'user_created', 'hostname_created')
#     readonly_fields = ('registered_subject', 'appointment')
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "lab_entry":
#             kwargs["queryset"] = LabEntry.objects.filter(pk=request.GET.get('lab_entry'))
#         return super(RequisitionMetaDataAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)
