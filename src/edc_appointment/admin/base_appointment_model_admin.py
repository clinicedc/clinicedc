from edc_base.modeladmin.admin import BaseModelAdmin

from ..models import Appointment


class BaseAppointmentModelAdmin(BaseModelAdmin):

    """ModelAdmin subclass for models with a ForeignKey to 'appointment', such as your visit model(s).

    In the child ModelAdmin class set the following attributes, for example::

        visit_attr = 'maternal_visit'
        dashboard_type = 'maternal'

    """
    date_hierarchy = 'report_datetime'

    def __init__(self, *args, **kwargs):
        super(BaseAppointmentModelAdmin, self).__init__(*args, **kwargs)
        self.list_display = ['appointment', 'report_datetime', 'reason', 'created',
                             'modified', 'user_created', 'user_modified', ]

        self.search_fields = ['id', 'reason', 'appointment__visit_definition__code',
                              'appointment__registered_subject__subject_identifier']

        self.list_filter = ['appointment__visit_instance',
                            'reason',
                            'appointment__visit_definition__code',
                            'appointment__registered_subject__study_site',
                            'report_datetime',
                            'created',
                            'modified',
                            'user_created',
                            'user_modified',
                            'hostname_created']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'appointment' and request.GET.get('appointment'):
            kwargs["queryset"] = Appointment.objects.filter(pk=request.GET.get('appointment', 0))
        return super(BaseAppointmentModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
