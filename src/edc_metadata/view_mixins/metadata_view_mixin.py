from django.contrib import messages
from django.utils.safestring import mark_safe
from edc_appointment.constants import IN_PROGRESS_APPT

from ..constants import CRF, NOT_REQUIRED, REQUISITION, REQUIRED, KEYED
from ..metadata_wrappers import CrfMetadataWrappers, RequisitionMetadataWrappers
from pprint import pprint


class MetaDataViewMixin:

    crf_model_wrapper_cls = None
    requisition_model_wrapper_cls = None
    crf_metadata_wrappers_cls = CrfMetadataWrappers
    requisition_metadata_wrappers_cls = RequisitionMetadataWrappers

    show_status = [REQUIRED, KEYED]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.appointment:
            if self.appointment.appt_status != IN_PROGRESS_APPT:
                self.message_user(mark_safe(
                    f'Wait!. Another user has switch the current appointment! '
                    f'<BR>Appointment {self.appointment} is no longer "in progress".'))
            crf_metadata_wrappers = self.crf_metadata_wrappers_cls(
                appointment=self.appointment)
            requisition_metadata_wrappers = self.requisition_metadata_wrappers_cls(
                appointment=self.appointment)
            context.update(
                report_datetime=self.appointment.visit.report_datetime,
                crfs=self.get_model_crf_wrapper(
                    key=CRF, metadata_wrappers=crf_metadata_wrappers),
                requisitions=self.get_model_requisition_wrapper(
                    key=REQUISITION, metadata_wrappers=requisition_metadata_wrappers),
                NOT_REQUIRED=NOT_REQUIRED)
        return context

    def message_user(self, message=None):
        messages.error(self.request, message=message)

    def get_model_crf_wrapper(self, key=None, metadata_wrappers=None):
        model_wrappers = []
        for metadata_wrapper in metadata_wrappers.objects:
            if not metadata_wrapper.model_obj:
                metadata_wrapper.model_obj = metadata_wrapper.model_cls(
                    **{metadata_wrapper.model_cls.visit_model_attr(): metadata_wrapper.visit})
            metadata_wrapper.metadata_obj.object = self.crf_model_wrapper_cls(
                model_obj=metadata_wrapper.model_obj,
                model=metadata_wrapper.metadata_obj.model,
                key=key)
            model_wrappers.append(metadata_wrapper.metadata_obj)
        return model_wrappers

    def get_model_requisition_wrapper(self, key=None, metadata_wrappers=None):
        model_wrappers = []
        for metadata_wrapper in metadata_wrappers.objects:
            if not metadata_wrapper.model_obj:
                metadata_wrapper.model_obj = metadata_wrapper.model_cls(
                    **{metadata_wrapper.model_cls.visit_model_attr(): metadata_wrapper.visit})
            metadata_wrapper.metadata_obj.object = self.requisition_model_wrapper_cls(
                model_obj=metadata_wrapper.model_obj,
                model=metadata_wrapper.metadata_obj.model,
                key=key,
                requisition_panel_name=metadata_wrapper.panel_name)
            model_wrappers.append(metadata_wrapper.metadata_obj)
        return model_wrappers
