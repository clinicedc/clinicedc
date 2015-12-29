from django.contrib import admin

from edc_visit_tracking.admin import BaseVisitTrackingModelAdmin

from ..actions import flag_as_received, flag_as_not_received, flag_as_not_labelled, print_requisition_label


class BaseRequisitionModelAdmin(BaseVisitTrackingModelAdmin):

    date_hierarchy = 'requisition_datetime'
    actions = [flag_as_received,
               flag_as_not_received,
               flag_as_not_labelled,
               print_requisition_label, ]

    def __init__(self, *args, **kwargs):
        super(BaseRequisitionModelAdmin, self).__init__(*args, **kwargs)
        self.fields = [
            self.visit_attr,
            "requisition_datetime",
            "is_drawn",
            "reason_not_drawn",
            "drawn_datetime",
            "site",
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
            "site": admin.VERTICAL,
        }
        self.list_display = [
            'requisition_identifier',
            # 'specimen_identifier',
            'subject',
            'visit',
            "requisition_datetime",
            "panel",
            'hostname_created',
            'is_receive',
            'aliquot',
            # 'is_labelled',
            # 'is_packed',
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
