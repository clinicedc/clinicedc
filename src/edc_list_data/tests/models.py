from edc_model.models.base_uuid_model import BaseUuidModel

from edc_list_data.model_mixins import BaseListModelMixin


class Antibiotic(BaseListModelMixin, BaseUuidModel):
    pass


class Neurological(BaseListModelMixin, BaseUuidModel):
    pass


class SignificantNewDiagnosis(BaseListModelMixin, BaseUuidModel):
    pass


class Symptom(BaseListModelMixin, BaseUuidModel):
    pass
