from edc.base.modeladmin.admin import BaseModelAdmin

from edc_appointment import Appointment


class BaseAppointmentModelAdmin(BaseModelAdmin):

    """ModelAdmin subclass for models with a ForeignKey to 'edc_appointment', such as your visit model(s).

    In the child ModelAdmin class set the following attributes, for example::

        visit_model_foreign_key = 'maternal_visit'
        dashboard_type = 'maternal'

    """
    date_hierarchy = 'report_datetime'

    def __init__(self, *args, **kwargs):

#         # dashboard_type is required to reverse url back to dashboard
#         if not hasattr(self, 'dashboard_type'):
#             raise AttributeError('{0} attribute \'dashboard_type\' is required but has not been defined.'.format(self))
#         elif not self.dashboard_type:
#             raise ValueError('{0} attribute \'dashboard_type\' cannot be None. '.format(self))
#         else:
#             pass

        super(BaseAppointmentModelAdmin, self).__init__(*args, **kwargs)

#         # edc_appointment key should exist, if not, maybe sent the wrong model
#         if not [f.name for f in self.model._meta.fields if f.name == 'edc_appointment']:
#             raise AttributeError('The model for BaseAppointmentModelAdmin child class {0} '
#                                  'requires model attribute \'edc_appointment\'. Not found '
#                                  'in model {1}.'.format(self, self.model._meta.object_name))

        self.list_display = ['edc_appointment', 'report_datetime', 'reason', 'created',
                             'modified', 'user_created', 'user_modified', ]

        self.search_fields = ['id', 'reason', 'appointment__visit_definition__code',
                              'appointment__registered_subject__subject_identifier']

        self.list_filter = ['appointment__visit_instance',
                            'reason',
                            'appointment__visit_definition__code',
                            'appointment__registered_subject__study_site__site_code',
                            'report_datetime',
                            'created',
                            'modified',
                            'user_created',
                            'user_modified',
                            'hostname_created']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'edc_appointment' and request.GET.get('edc_appointment'):
            kwargs["queryset"] = Appointment.objects.filter(pk=request.GET.get('edc_appointment', 0))
        return super(BaseAppointmentModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
