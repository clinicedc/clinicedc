from edc_adverse_event.model_mixins import AeInitialModelMixin
from edc_adverse_event.pdf_reports import AePdfReport
from edc_model.models import BaseUuidModel


class AeInitial(AeInitialModelMixin, BaseUuidModel):
    pdf_report_cls = AePdfReport

    class Meta(AeInitialModelMixin.Meta, BaseUuidModel.Meta):
        pass
