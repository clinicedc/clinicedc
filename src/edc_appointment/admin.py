from django.contrib import admin

from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_base.modeladmin_mixins import (
    ModelAdminFormInstructionsMixin, ModelAdminNextUrlRedirectMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin,
    audit_fieldset_tuple)

from .admin_site import edc_appointment_admin
from .models import Holiday, Appointment


@admin.register(Appointment, site=edc_appointment_admin)
class AppointmentAdmin(ModelAdminFormInstructionsMixin, ModelAdminNextUrlRedirectMixin,
                       ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin,
                       ModelAdminAuditFieldsMixin,
                       ModelAdminReadOnlyMixin, admin.ModelAdmin):

    date_hierarchy = 'appt_datetime'
    list_display = ('subject_identifier', 'visit_code',
                    'appt_datetime', 'appt_type', 'appt_status')

    fieldsets = (
        (None, ({
            'fields': (
                'appt_datetime',
                'appt_type',
                'appt_status',
                'appt_reason',
                'comment')})),
        audit_fieldset_tuple,
    )

    radio_fields = {
        'appt_type': admin.VERTICAL,
        'appt_status': admin.VERTICAL}

    list_filter = ('visit_code', 'appt_datetime', 'appt_type', 'appt_status')


@admin.register(Holiday, site=edc_appointment_admin)
class HolidayAdmin(admin.ModelAdmin):

    date_hierarchy = 'day'
    list_display = ('name', 'day', )
