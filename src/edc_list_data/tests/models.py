from edc_list_data.model_mixins import ListModelMixin
from edc_model.models.base_uuid_model import BaseUuidModel


class Antibiotic(ListModelMixin, BaseUuidModel):
    pass


class Neurological(ListModelMixin, BaseUuidModel):
    pass


class SignificantNewDiagnosis(ListModelMixin, BaseUuidModel):
    pass


class Symptom(ListModelMixin, BaseUuidModel):
    pass
