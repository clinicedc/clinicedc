from django.conf import settings
from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from edc_model_admin.model_admin_audit_fields_mixin import audit_fieldset_tuple,\
    audit_fields
from edc_visit_schedule.fieldsets import visit_schedule_fieldset_tuple,\
    visit_schedule_fields


class CrfModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to your
    visit model(s).
    """

    date_hierarchy = 'report_datetime'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display = list(self.list_display)
        self.list_display.append(self.visit_model_attr)
        self.list_display = tuple(self.list_display)
        self.extend_search_fields()
        self.extend_list_filter()

    @property
    def visit_model(self):
        return self.model.visit_model_cls()

    @property
    def visit_model_attr(self):
        return self.model.visit_model_attr()

    def extend_search_fields(self):
        self.search_fields = list(self.search_fields)
        self.search_fields.extend([
            f'{self.visit_model_attr}__appointment__subject_identifier'])
        self.search_fields = tuple(set(self.search_fields))

    def extend_list_filter(self):
        """Extends list filter with additional values from the visit
        model.
        """
        self.list_filter = list(self.list_filter)
        self.list_filter.extend([
            self.visit_model_attr + '__report_datetime',
            self.visit_model_attr + '__reason',
            self.visit_model_attr + '__appointment__appt_status',
            self.visit_model_attr + '__appointment__visit_code'])
        self.list_filter = tuple(self.list_filter)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == self.visit_model_attr:
            if request.GET.get(self.visit_model_attr):
                kwargs["queryset"] = self.visit_model.objects.filter(
                    id__exact=request.GET.get(self.visit_model_attr, 0))
            else:
                kwargs["queryset"] = self.visit_model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class VisitModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to
    'appointment', such as your visit model(s).

    In the child ModelAdmin class set the following attributes,
    for example:

        visit_attr = 'maternal_visit'
        dashboard_type = 'maternal'
    """
    date_hierarchy = 'report_datetime'

    fieldsets = (
        (None, {
            'fields': [
                'appointment',
                'report_datetime',
                'reason',
                'reason_missed',
                'reason_unscheduled',
                'reason_unscheduled_other',
                'info_source',
                'info_source_other',
                'comments'
            ]}),
        visit_schedule_fieldset_tuple,
        audit_fieldset_tuple
    )

    radio_fields = {
        'reason': admin.VERTICAL,
        'reason_unscheduled': admin.VERTICAL,
        'reason_missed': admin.VERTICAL,
        'info_source': admin.VERTICAL,
        'require_crfs': admin.VERTICAL}

    list_display = ['appointment', 'subject_identifier', 'report_datetime',
                    'reason',
                    'study_status', 'require_crfs', 'created',
                    'modified', 'user_created',
                    'user_modified', ]

    search_fields = ['id', 'reason', 'appointment__visit_code',
                     'appointment__subject_identifier']

    list_filter = [
        'report_datetime',
        'appointment__visit_code',
        'appointment__visit_code_sequence',
        'reason',
        'require_crfs',
        'created',
        'modified',
        'user_created',
        'user_modified',
        'hostname_created']

    def subject_identifier(self, obj=None):
        return obj.appointment.subject_identifier

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'appointment':
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get('appointment', 0))
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = fields + audit_fields + visit_schedule_fields
        return fields

    def view_on_site(self, obj):
        dashboard_url_name = settings.DASHBOARD_URL_NAMES.get(
            'subject_dashboard_url')
        try:
            return reverse(
                dashboard_url_name, kwargs=dict(
                    subject_identifier=obj.subject_identifier,
                    appointment=str(obj.appointment.id)))
        except NoReverseMatch:
            return super().view_on_site(obj)


class CareTakerFieldsAdminMixin:

    mixin_fields = [
        'information_provider',
        'information_provider_other',
        'is_present',
        'survival_status',
        'last_alive_date',
        'comments']
    radio_fields_mixin = {
        'is_present': admin.VERTICAL,
        'survival_status': admin.VERTICAL,
    }
