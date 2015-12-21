from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin
from edc.subject.registration.models import RegisteredSubject

from ..forms import AppointmentForm
from ..models import Appointment

from .pre_appointment_contact_admin import PreAppointmentContactInlineAdmin


class AppointmentAdmin(BaseModelAdmin):

    """ModelAdmin class to handle appointments."""

    form = AppointmentForm
    date_hierarchy = 'appt_datetime'
    inlines = [PreAppointmentContactInlineAdmin, ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limits the dropdown for 'registered_subject'"""
        if db_field.name == "registered_subject":
            if request.GET.get('registered_subject'):
                kwargs["queryset"] = RegisteredSubject.objects.filter(pk=request.GET.get('registered_subject'))
            else:
                self.readonly_fields = list(self.readonly_fields)
                try:
                    self.readonly_fields.index('registered_subject')
                except ValueError:
                    self.readonly_fields.append('registered_subject')
        return super(AppointmentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    fields = (
        'registered_subject',
        'appt_datetime',
        'appt_status',
        'study_site',
        'visit_definition',
        'visit_instance',
        'appt_type',
    )

    search_fields = ('registered_subject__subject_identifier', 'id')

    list_display = (
        'registered_subject',
        'dashboard',
        'appt_datetime',
        'appt_type',
        'appt_status',
        'is_confirmed',
        'contact_count',
        'visit_definition',
        'visit_instance',
        'best_appt_datetime',
        'created',
        'hostname_created')

    list_filter = (
        'study_site',
        'registered_subject__subject_type',
        'appt_type',
        'is_confirmed',
        'contact_count',
        'appt_datetime',
        'appt_status',
        'visit_instance',
        'visit_definition',
        'created',
        'user_created',
        'hostname_created')

    radio_fields = {
        "appt_status": admin.VERTICAL,
        'study_site': admin.VERTICAL,
        'appt_type': admin.VERTICAL}

admin.site.register(Appointment, AppointmentAdmin)
