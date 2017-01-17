from django.contrib import admin


class CrfModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to your visit model(s)"""

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
        return self.model.visit_model()

    @property
    def visit_model_attr(self):
        return self.model.visit_model_attr()

    def extend_search_fields(self):
        self.search_fields = list(self.search_fields)
        self.search_fields.extend([
            '{}__appointment__subject_identifier'.format(self.visit_model_attr)])
        self.search_fields = tuple(set(self.search_fields))

    def extend_list_filter(self):
        """Extends list filter with additional values from the visit model."""
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
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class VisitModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to 'appointment', such as your visit model(s).

    In the child ModelAdmin class set the following attributes, for example::

        visit_attr = 'maternal_visit'
        dashboard_type = 'maternal'

    """
    date_hierarchy = 'report_datetime'

    fields = [
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
    list_display = ['appointment', 'report_datetime', 'reason', 'study_status', 'created',
                    'modified', 'user_created', 'user_modified', ]

    search_fields = ['id', 'reason', 'appointment__visit_code',
                     'appointment__subject_identifier']

    list_filter = [
        'study_status',
        'appointment__visit_instance',
        'reason',
        'appointment__visit_code',
        'report_datetime',
        'created',
        'modified',
        'user_created',
        'user_modified',
        'hostname_created']
    radio_fields = {'require_crfs': admin.VERTICAL}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'appointment' and request.GET.get('appointment'):
            kwargs["queryset"] = db_field.related_model.objects.filter(pk=request.GET.get('appointment', 0))
        return super(VisitModelAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)


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
