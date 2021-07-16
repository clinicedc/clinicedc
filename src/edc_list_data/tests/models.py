from django.db import models
from edc_model.models.base_uuid_model import BaseUuidModel

from edc_list_data.model_mixins import BaseListModelMixin


class Antibiotic(BaseListModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class Neurological(BaseListModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class SignificantNewDiagnosis(BaseListModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class Symptom(BaseListModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class Consignee(BaseUuidModel):

    name = models.CharField(max_length=25)

    contact = models.CharField(max_length=25)

    address = models.CharField(max_length=25)

    class Meta(BaseUuidModel.Meta):
        pass


class Customer(BaseUuidModel):

    name = models.CharField(max_length=25, unique=True)

    contact = models.CharField(max_length=25)

    address = models.CharField(max_length=25)

    class Meta(BaseUuidModel.Meta):
        pass
