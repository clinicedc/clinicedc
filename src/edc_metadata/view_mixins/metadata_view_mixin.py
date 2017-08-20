from ..constants import CRF, NOT_REQUIRED, REQUISITION
from ..metaforms import CrfMetaforms, RequisitionMetaforms


class MetaDataViewMixin:

    crf_model_wrapper_cls = None
    requisition_model_wrapper_cls = None
    crf_metaforms_cls = CrfMetaforms
    requisition_metaforms_cls = RequisitionMetaforms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.appointment:
            crf_metaforms = self.crf_metaforms_cls(
                appointment=self.appointment)
            requisition_metaforms = self.requisition_metaforms_cls(
                appointment=self.appointment)
            context.update(
                report_datetime=self.appointment.visit.report_datetime,
                crfs=self.get_model_wrappers(key=CRF, metaforms=crf_metaforms),
                requisitions=self.get_model_wrappers(
                    key=REQUISITION, metaforms=requisition_metaforms),
                NOT_REQUIRED=NOT_REQUIRED)
        return context

    def get_model_wrappers(self, key=None, metaforms=None):
        model_wrappers = []
        for metaform in metaforms.objects:
            if not metaform.model_obj:
                metaform.model_obj = metaform.model_cls(
                    **{metaform.model_cls.visit_model_attr(): metaform.visit})
            metaform.metadata_obj.object = self.crf_model_wrapper_cls(
                model_obj=metaform.model_obj,
                model=metaform.metadata_obj.model,
                key=key)
            model_wrappers.append(metaform.metadata_obj)
        return model_wrappers
