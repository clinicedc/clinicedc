from django.conf import settings
from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_base.sites.admin import ModelAdminSiteMixin
from edc_model_admin import (
    ModelAdminFormInstructionsMixin, ModelAdminNextUrlRedirectMixin,
    ModelAdminFormAutoNumberMixin, ModelAdminRedirectOnDeleteMixin,
    ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin,
    audit_fieldset_tuple)
from edc_visit_schedule.fieldsets import visit_schedule_fieldset_tuple, visit_schedule_fields

from ..admin_site import edc_appointment_admin
from ..forms import AppointmentForm
from ..models import Appointment


@admin.register(Appointment, site=edc_appointment_admin)
class AppointmentAdmin(ModelAdminFormInstructionsMixin, ModelAdminNextUrlRedirectMixin,
                       ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin,
                       ModelAdminAuditFieldsMixin, ModelAdminRedirectOnDeleteMixin,
                       ModelAdminReadOnlyMixin, ModelAdminSiteMixin, admin.ModelAdmin):

    post_url_on_delete_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    dashboard_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')

    form = AppointmentForm
    date_hierarchy = 'appt_datetime'
    list_display = ('subject_identifier', '__str__',
                    'appt_datetime', 'appt_type', 'appt_status')
    list_filter = ('visit_code', 'appt_datetime', 'appt_type', 'appt_status')

    additional_instructions = mark_safe(
        'To start or continue to edit FORMS for this subject, change the '
        'appointment status below to "In Progress" and click SAVE. <BR>'
        '<i>Note: You may only edit one appointment at a time. '
        'Before you move to another appointment, change the appointment '
        'status below to "Incomplete or "Done".</i>')

    fieldsets = (
        (None, ({
            'fields': (
                'subject_identifier',
                'appt_datetime',
                'appt_type',
                'appt_status',
                'appt_reason',
                'comment')})),
        ('Timepoint', ({
            'classes': ('collapse',),
            'fields': (
                'timepoint',
                'timepoint_datetime',
                'visit_code_sequence',
                'facility_name')})),
        visit_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        'appt_type': admin.VERTICAL,
        'appt_status': admin.VERTICAL,
        'appt_reason': admin.VERTICAL
    }

    def post_url_on_delete_kwargs(self, request, obj):
        return dict(subject_identifier=obj.subject_identifier)

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj)
                + visit_schedule_fields
                + ('subject_identifier', 'timepoint', 'timepoint_datetime',
                   'visit_code_sequence', 'facility_name'))

    def view_on_site(self, obj):
        try:
            url = reverse(
                self.dashboard_url_name, kwargs=dict(
                    subject_identifier=obj.subject_identifier))
        except NoReverseMatch:
            url = super().view_on_site(obj)
        return url
