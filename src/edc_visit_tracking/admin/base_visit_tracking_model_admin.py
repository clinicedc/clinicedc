from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured

from edc.export.actions import export_as_csv_action
from edc_base.modeladmin.admin import BaseModelAdmin


class BaseVisitTrackingModelAdmin(BaseModelAdmin):

    """ModelAdmin subclass for models with a ForeignKey to your visit model(s)"""

    visit_model = None
    visit_attr = None
    date_hierarchy = 'report_datetime'

    def __init__(self, *args, **kwargs):
        super(BaseVisitTrackingModelAdmin, self).__init__(*args, **kwargs)
        if not self.visit_model:
            raise ImproperlyConfigured('Class attribute \'visit model\' on BaseVisitModelAdmin '
                                       'for model {0} may not be None. Please correct.'.format(self.model))
        if not self.visit_attr:
            raise ValueError(
                'The admin class for \'{0}\' needs to know the field attribute that points to \'{1}\'. '
                'Specify this on the ModelAdmin class as \'visit_attr\'.'.format(
                    self.model._meta.model._meta.verbose_name, self.visit_model._meta.verbose_name))
        self.list_display = list(self.list_display)
        self.list_display.append(self.visit_attr)
        self.list_display = tuple(self.list_display)
        self.extend_search_fields()
        self.extend_list_filter()

    def extend_search_fields(self):
        self.search_fields = list(self.search_fields)
        self.search_fields.extend([
            '{}__appointment__registered_subject__identity'.format(self.visit_attr),
            '{}__appointment__registered_subject__first_name'.format(self.visit_attr),
            '{}__appointment__registered_subject__subject_identifier'.format(self.visit_attr)])
        self.search_fields = tuple(set(self.search_fields))

    def extend_list_filter(self):
        """Extends list filter with additional values from the visit model."""
        self.list_filter = list(self.list_filter)
        self.list_filter.extend([
            self.visit_attr + '__report_datetime',
            self.visit_attr + '__reason',
            self.visit_attr + '__appointment__appt_status',
            self.visit_attr + '__appointment__visit_definition__code',
            self.visit_attr + '__appointment__registered_subject__study_site__site_code'])
        self.list_filter = tuple(self.list_filter)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == self.visit_attr:
            if request.GET.get(self.visit_attr):
                kwargs["queryset"] = self.visit_model.objects.filter(id__exact=request.GET.get(self.visit_attr, 0))
            else:
                self.readonly_fields = list(self.readonly_fields)
                try:
                    self.readonly_fields.index(self.visit_attr)
                except ValueError:
                    self.readonly_fields.append(self.visit_attr)
        return super(BaseVisitTrackingModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_actions(self, request):
        actions = super(BaseVisitTrackingModelAdmin, self).get_actions(request)
        actions['export_as_csv_action'] = (
            export_as_csv_action(
                exclude=['id', self.visit_attr],
                extra_fields=OrderedDict(
                    {'subject_identifier':
                     '{}__appointment__registered_subject__subject_identifier'.format(self.visit_attr),
                     'visit_report_datetime': '{}__report_datetime'.format(self.visit_attr),
                     'gender': '{}__appointment__registered_subject__gender'.format(self.visit_attr),
                     'dob': '{}__appointment__registered_subject__dob'.format(self.visit_attr),
                     'visit_reason': '{}__reason.format(self.visit_attr)'.format(self.visit_attr),
                     'visit_status': '{}__appointment__appt_status'.format(self.visit_attr),
                     'visit': '{}__appointment__visit_definition__code'.format(self.visit_attr),
                     'visit_instance': '{}__appointment__visit_instance'.format(self.visit_attr)}),
            ),
            'export_as_csv_action',
            'Export to CSV with visit and demographics')
        return actions
