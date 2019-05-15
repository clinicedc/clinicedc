from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin
from edc_appointment.constants import IN_PROGRESS_APPT
from edc_dashboard.view_mixins import MessageViewMixin
from edc_subject_model_wrappers import RequisitionModelWrapper, CrfModelWrapper

from ..constants import CRF, NOT_REQUIRED, REQUISITION, REQUIRED, KEYED
from ..metadata_wrappers import CrfMetadataWrappers, RequisitionMetadataWrappers


class MetaDataViewError(Exception):
    pass


class MetaDataViewMixin(MessageViewMixin, ContextMixin):

    crf_model_wrapper_cls = CrfModelWrapper
    requisition_model_wrapper_cls = RequisitionModelWrapper
    crf_metadata_wrappers_cls = CrfMetadataWrappers
    requisition_metadata_wrappers_cls = RequisitionMetadataWrappers
    panel_model = "edc_lab.panel"

    metadata_show_status = [REQUIRED, KEYED]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(metadata_show_status=self.metadata_show_status)
        if self.appointment:
            if self.appointment.appt_status != IN_PROGRESS_APPT:
                message = _(
                    'You have selected a visit that is no longer "in progress". '
                    "Refer to the schedule for the visit that is "
                    'currently "in progress".'
                )
                self.message_user(message, level=messages.WARNING)

            context.update(
                report_datetime=self.appointment.visit.report_datetime,
                crfs=self.get_crf_model_wrappers(),
                requisitions=self.get_requisition_model_wrapper(),
                NOT_REQUIRED=NOT_REQUIRED,
                REQUIRED=REQUIRED,
                KEYED=KEYED,
            )
        return context

    def get_crf_model_wrappers(self):
        """Returns a list of model wrappers.
        """
        model_wrappers = []
        crf_metadata_wrappers = self.crf_metadata_wrappers_cls(
            appointment=self.appointment
        )
        for metadata_wrapper in crf_metadata_wrappers.objects:
            if not metadata_wrapper.model_obj:
                metadata_wrapper.model_obj = metadata_wrapper.model_cls(
                    **{
                        metadata_wrapper.model_cls.visit_model_attr(): metadata_wrapper.visit
                    }
                )
            metadata_wrapper.metadata_obj.object = self.crf_model_wrapper_cls(
                model_obj=metadata_wrapper.model_obj,
                model=metadata_wrapper.metadata_obj.model,
                key=CRF,
                request=self.request,
            )
            model_wrappers.append(metadata_wrapper.metadata_obj)
        return [
            model_wrapper
            for model_wrapper in model_wrappers
            if model_wrapper.entry_status in self.metadata_show_status
        ]

    def get_requisition_model_wrapper(self):
        """Returns a list of model wrappers.
        """
        model_wrappers = []
        requisition_metadata_wrappers = self.requisition_metadata_wrappers_cls(
            appointment=self.appointment
        )
        for metadata_wrapper in requisition_metadata_wrappers.objects:
            if not metadata_wrapper.model_obj:
                panel = self.get_panel(metadata_wrapper)
                metadata_wrapper.model_obj = metadata_wrapper.model_cls(
                    **{
                        metadata_wrapper.model_cls.visit_model_attr(): metadata_wrapper.visit,
                        "panel": panel,
                    }
                )
            metadata_wrapper.metadata_obj.object = self.requisition_model_wrapper_cls(
                model_obj=metadata_wrapper.model_obj,
                model=metadata_wrapper.metadata_obj.model,
                key=REQUISITION,
                request=self.request,
            )
            model_wrappers.append(metadata_wrapper.metadata_obj)
        return [
            model_wrapper
            for model_wrapper in model_wrappers
            if model_wrapper.entry_status in self.metadata_show_status
        ]

    def get_panel(self, metadata_wrapper=None):
        try:
            panel = self.panel_model_cls.objects.get(name=metadata_wrapper.panel_name)
        except ObjectDoesNotExist as e:
            raise MetaDataViewError(
                f"{e} Got panel name '{metadata_wrapper.panel_name}'. "
                f"See {metadata_wrapper}."
            )
        return panel

    @property
    def panel_model_cls(self):
        return django_apps.get_model(self.panel_model)
