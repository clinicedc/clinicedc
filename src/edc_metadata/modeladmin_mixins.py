
class Base:

    def seq(self, obj=None):
        return obj.visit_code_sequence


class CrfMetaDataAdminMixin(Base):

    search_fields = (
        'subject_identifier', 'model', 'id')
    list_display = (
        'subject_identifier', 'model', 'visit_code', 'seq', 'entry_status', 'fill_datetime',
        'due_datetime', 'close_datetime', 'created', 'hostname_created')
    list_filter = (
        'entry_status', 'visit_code', 'visit_code_sequence', 'schedule_name',
        'visit_schedule_name', 'model', 'fill_datetime', 'created',
        'user_created', 'hostname_created')
    readonly_fields = ('subject_identifier', 'model', 'visit_code',
                       'schedule_name', 'visit_schedule_name',
                       'show_order', 'current_entry_title')


class RequisitionMetaDataAdminMixin(Base):

    search_fields = (
        'subject_identifier', 'model', 'id', 'panel_name')
    list_display = (
        'subject_identifier', 'model', 'panel', 'visit_code', 'seq',
        'entry_status', 'fill_datetime', 'due_datetime', 'close_datetime',
        'created', 'hostname_created')
    list_filter = (
        'entry_status', 'panel_name', 'visit_code', 'visit_code_sequence',
        'schedule_name', 'visit_schedule_name', 'model', 'fill_datetime',
        'created', 'user_created', 'hostname_created')
    readonly_fields = ('subject_identifier', 'model', 'visit_code',
                       'schedule_name', 'visit_schedule_name',
                       'show_order', 'current_entry_title')

    def panel(self, obj=None):
        return obj.panel_name
