# from collections import OrderedDict

from django.db.models import ForeignKey
from django.core.exceptions import ImproperlyConfigured

from edc_base.modeladmin.admin import BaseModelAdmin
# from edc.export.actions import export_as_csv_action
# from edc_consent.models import BaseConsentedUuidModel

from ..classes import VisitModelHelper
from ..mixins import VisitTrackingAdminMixin


class BaseVisitTrackingModelAdmin(VisitTrackingAdminMixin, BaseModelAdmin):

    """ModelAdmin subclass for models with a ForeignKey to your visit model(s)"""

    date_hierarchy = 'report_datetime'
    visit_model = None
    visit_model_field_name = None

    def __init__(self, *args, **kwargs):
        super(BaseVisitTrackingModelAdmin, self).__init__(*args, **kwargs)
        if not self.visit_model:
            raise ImproperlyConfigured(
                'Class attribute \'visit model\' on BaseVisitModelAdmin '
                'for model {0} may not be None. Please correct.'.format(self.model))
        if not self.visit_model_field_name:
            raise ImproperlyConfigured(
                'Class attribute \'visit_model_field_name model\' on BaseVisitModelAdmin '
                'for model {0} may not be None. Please correct.'.format(self.model))

#     def get_actions(self, request):
#         actions = super(BaseVisitTrackingModelAdmin, self).get_actions(request)
#         if issubclass(self.model, BaseConsentedUuidModel):
#             actions['export_as_csv_action'] = (  # This is a django SortedDict (function, name, short_description)
#                 export_as_csv_action(
#                     exclude=['id', self.visit_model_field_name],
#                     extra_fields=OrderedDict(
#                         {'subject_identifier': ('{}__appointment__registered_subject'
#                                                 '__subject_identifier').format(self.visit_model_field_name),
#                          'visit_report_datetime': '%s__report_datetime' % self.visit_model_field_name,
#                          'gender': self.visit_model_field_name + '__appointment__registered_subject__gender',
#                          'dob': self.visit_model_field_name + '__appointment__registered_subject__dob',
#                          'visit_reason': self.visit_model_field_name + '__reason',
#                          'visit_status': self.visit_model_field_name + '__appointment__appt_status',
#                          'visit': self.visit_model_field_name + '__appointment__visit_definition__code',
#                          'visit_instance': self.visit_model_field_name + '__appointment__visit_instance'}),
#                     ),
#                 'export_as_csv_action',
#                 'Export to CSV with visit and demographics')
#         return actions

    def add_view(self, request, form_url='', extra_context=None):
        """Sets the values for the visit model object name and the visit model pk.

        To be used by supplemental fields, etc."""
        self.visit_model_attr = request.GET.get('visit_attr')
        self.visit_model_pk = request.GET.get(self.visit_model_attr)
        return super(BaseVisitTrackingModelAdmin, self).add_view(
            request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Sets the values for the visit model object name and the visit model pk.

        To be used by supplemental fields, etc."""
        self.visit_model_attr = request.GET.get('visit_attr')
        self.visit_model_pk = request.GET.get(self.visit_model_attr)
        return super(BaseVisitTrackingModelAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        visit_model_helper = VisitModelHelper()
        if db_field.name == visit_model_helper.get_visit_field(model=self.model, visit_model=self.visit_model):
            kwargs["queryset"] = visit_model_helper.set_visit_queryset(
                visit_model=self.visit_model,
                pk=request.GET.get(db_field.name, None),
                subject_identifier=request.GET.get('subject_identifier', 0),
                visit_code=request.GET.get('visit_code', 0),
                visit_instance=request.GET.get('visit_instance', 0))
        return super(BaseVisitTrackingModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
