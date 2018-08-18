from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.views.generic.base import ContextMixin
from edc_appointment.constants import IN_PROGRESS_APPT
from edc_visit_schedule.model_wrappers import RequisitionModelWrapper, CrfModelWrapper

from ..constants import CRF, NOT_REQUIRED, REQUISITION, REQUIRED, KEYED
from ..metadata_wrappers import CrfMetadataWrappers, RequisitionMetadataWrappers


class MetaDataViewError(Exception):
    pass


class MetaDataViewMixin(ContextMixin):

    crf_model_wrapper_cls = CrfModelWrapper
    requisition_model_wrapper_cls = RequisitionModelWrapper
    crf_metadata_wrappers_cls = CrfMetadataWrappers
    requisition_metadata_wrappers_cls = RequisitionMetadataWrappers
    panel_model = 'edc_lab.panel'

    metadata_show_status = [REQUIRED, KEYED]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(metadata_show_status=self.metadata_show_status)
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
                crfs=[
                    crf for crf in self.get_crf_model_wrapper(
                        key=CRF, metadata_wrappers=crf_metadata_wrappers)
                    if crf.entry_status in self.metadata_show_status],
                requisitions=[
                    requisition for requisition in self.get_requisition_model_wrapper(
                        key=REQUISITION, metadata_wrappers=requisition_metadata_wrappers)
                    if requisition.entry_status in self.metadata_show_status],
                NOT_REQUIRED=NOT_REQUIRED,
                REQUIRED=REQUIRED,
                KEYED=KEYED)
        return context

    def message_user(self, message=None):
        messages.error(self.request, message=message)

    def get_crf_model_wrapper(self, key=None, metadata_wrappers=None):
        model_wrappers = []
        for metadata_wrapper in metadata_wrappers.objects:
            if not metadata_wrapper.model_obj:
                metadata_wrapper.model_obj = metadata_wrapper.model_cls(
                    **{metadata_wrapper.model_cls.visit_model_attr(): metadata_wrapper.visit})
            metadata_wrapper.metadata_obj.object = self.crf_model_wrapper_cls(
                model_obj=metadata_wrapper.model_obj,
                model=metadata_wrapper.metadata_obj.model,
                key=key,
                request=self.request)
            model_wrappers.append(metadata_wrapper.metadata_obj)
        return model_wrappers

    def get_requisition_model_wrapper(self, key=None, metadata_wrappers=None):
        model_wrappers = []
        for metadata_wrapper in metadata_wrappers.objects:
            if not metadata_wrapper.model_obj:
                panel = self.get_panel(metadata_wrapper)
                metadata_wrapper.model_obj = metadata_wrapper.model_cls(
                    **{metadata_wrapper.model_cls.visit_model_attr(): metadata_wrapper.visit,
                       'panel': panel})
            metadata_wrapper.metadata_obj.object = self.requisition_model_wrapper_cls(
                model_obj=metadata_wrapper.model_obj,
                model=metadata_wrapper.metadata_obj.model,
                key=key,
                request=self.request)
            model_wrappers.append(metadata_wrapper.metadata_obj)
        return model_wrappers

    def get_panel(self, metadata_wrapper=None):
        try:
            panel = self.panel_model_cls.objects.get(
                name=metadata_wrapper.panel_name)
        except ObjectDoesNotExist as e:
            raise MetaDataViewError(
                f'{e} Got panel name \'{metadata_wrapper.panel_name}\'. '
                f'See {metadata_wrapper}.')
        return panel

    @property
    def panel_model_cls(self):
        return django_apps.get_model(self.panel_model)
