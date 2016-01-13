from django.contrib import admin

from django.contrib.admin.views import main

from edc_export.actions import export_as_csv_action
from edc_visit_tracking.admin import VisitAdminMixin

from .actions import flag_as_received, flag_as_not_received, flag_as_not_labelled, print_requisition_label
from django.core.exceptions import ImproperlyConfigured


class RequisitionAdminMixin(VisitAdminMixin):

    panel_model = None
    date_hierarchy = 'requisition_datetime'
    actions = [flag_as_received,
               flag_as_not_received,
               flag_as_not_labelled,
               print_requisition_label, ]

    def __init__(self, *args, **kwargs):
        if not self.panel_model:
            raise ImproperlyConfigured('{}.panel_model cannot be None.'.format(self.__class__.__name__))
        super(RequisitionAdminMixin, self).__init__(*args, **kwargs)

        self.fields = [
            self.visit_attr,
            "requisition_datetime",
            "is_drawn",
            "reason_not_drawn",
            "drawn_datetime",
            'study_site',
            "panel",
            "test_code",
            "aliquot_type",
            "item_type",
            "item_count_total",
            "estimated_volume",
            "priority",
            "comments", ]

        self.radio_fields = {
            "is_drawn": admin.VERTICAL,
            "reason_not_drawn": admin.VERTICAL,
            "item_type": admin.VERTICAL,
            "priority": admin.VERTICAL,
        }

        self.list_display = [
            'requisition_identifier',
            # 'specimen_identifier',
            'subject',
            'visit',
            "requisition_datetime",
            "panel",
            'aliquot',
            'is_receive',
            'is_labelled',
            'is_packed',
            'hostname_created',
            # 'is_lis',
            # 'is_receive_datetime',
            # 'is_labelled_datetime',
        ]
        self.list_filter = [
            "priority",
            # 'is_receive',
            # 'is_labelled',
            'is_packed',
            # 'is_lis',
            'panel',
            "requisition_datetime",
            'study_site',
            # 'is_receive_datetime',
            # 'is_labelled_datetime',
            'user_created',
            'hostname_created',
            'user_modified',
        ]
        self.search_fields = [
            '{0}__appointment__registered_subject__subject_identifier'.format(self.visit_attr,),
            'specimen_identifier',
            'requisition_identifier',
            'panel__name']
        self.filter_horizontal = ["test_code", ]

    actions = [print_requisition_label,
               export_as_csv_action(
                   "Export as csv", fields=[], delimiter=',', exclude=[
                       'id', 'revision', 'hostname_created', 'hostname_modified',
                       'user_created', 'user_modified'],)]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        panel_pk = request.GET.get('panel', 0)
        if db_field.name == 'panel':
            kwargs["queryset"] = self.panel_model.objects.filter(pk=panel_pk)
        if db_field.name == 'aliquot_type':
            if self.panel_model.objects.filter(pk=panel_pk):
                if self.panel_model.objects.get(pk=panel_pk).aliquot_type.all():
                    kwargs["queryset"] = self.panel_model.objects.get(pk=panel_pk).aliquot_type.all()
        return super(RequisitionAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)
