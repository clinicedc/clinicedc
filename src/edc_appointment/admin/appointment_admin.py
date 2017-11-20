from django.contrib import admin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin import (
    ModelAdminFormInstructionsMixin, ModelAdminNextUrlRedirectMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin,
    audit_fieldset_tuple)
from edc_visit_schedule.admin import visit_schedule_fieldset_tuple,\
    visit_schedule_fields

from ..admin_site import edc_appointment_admin
from ..models import Appointment
from ..forms import AppointmentForm


@admin.register(Appointment, site=edc_appointment_admin)
class AppointmentAdmin(ModelAdminFormInstructionsMixin, ModelAdminNextUrlRedirectMixin,
                       ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin,
                       ModelAdminAuditFieldsMixin,
                       ModelAdminReadOnlyMixin, admin.ModelAdmin):

    form = AppointmentForm
    date_hierarchy = 'appt_datetime'
    list_display = ('subject_identifier', 'visit_code',
                    'appt_datetime', 'appt_type', 'appt_status')
    list_filter = ('visit_code', 'appt_datetime', 'appt_type', 'appt_status')

    fieldsets = (
        (None, ({
            'fields': (
                'subject_identifier',
                'appt_datetime',
                'appt_type',
                'appt_status',
                'appt_reason',
                'comment')})),
        visit_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        'appt_type': admin.VERTICAL,
        'appt_status': admin.VERTICAL,
        'appt_reason': admin.VERTICAL
    }

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj)
                + visit_schedule_fields
                + ('subject_identifier',))
