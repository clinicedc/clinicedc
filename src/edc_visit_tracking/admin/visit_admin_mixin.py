from django.contrib import admin

from edc_appointment.models import Appointment

from ..models import CaretakerFieldsMixin


class VisitAdminMixin(object):

    """ModelAdmin subclass for models with a ForeignKey to 'appointment', such as your visit model(s).

    In the child ModelAdmin class set the following attributes, for example::

        visit_attr = 'maternal_visit'
        dashboard_type = 'maternal'

    """
    date_hierarchy = 'report_datetime'

    def __init__(self, *args, **kwargs):
        super(VisitAdminMixin, self).__init__(*args, **kwargs)

        self.fields = [
            'appointment',
            'report_datetime',
            'reason',
            'reason_missed',
            'study_status',
            'require_crfs',
            'info_source',
            'info_source_other',
            'comments'
        ]
        if issubclass(self.model, CaretakerFieldsMixin):
            self.fields.pop(self.fields.index('comments'))
            self.fields.extend([
                'information_provider',
                'information_provider_other',
                'is_present',
                'survival_status',
                'last_alive_date',
                'comments'])

        self.list_display = ['appointment', 'report_datetime', 'reason', 'study_status', 'created',
                             'modified', 'user_created', 'user_modified', ]

        self.search_fields = ['id', 'reason', 'appointment__visit_definition__code',
                              'appointment__registered_subject__subject_identifier']

        self.list_filter = ['study_status',
                            'appointment__visit_instance',
                            'reason',
                            'appointment__visit_definition__code',
                            'appointment__registered_subject__study_site',
                            'report_datetime',
                            'created',
                            'modified',
                            'user_created',
                            'user_modified',
                            'hostname_created']
        self.radio_fields = {'require_crfs': admin.VERTICAL}
        if issubclass(self.model, CaretakerFieldsMixin):
            self.radio_fields.update({
                #'information_provider': admin.VERTICAL,
                'is_present': admin.VERTICAL,
                'survival_status': admin.VERTICAL,
            })

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'appointment' and request.GET.get('appointment'):
            kwargs["queryset"] = Appointment.objects.filter(pk=request.GET.get('appointment', 0))
        return super(VisitAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)
