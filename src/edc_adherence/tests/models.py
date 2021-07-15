from edc_crf.model_mixins import CrfModelMixin
from edc_model import models as edc_models

from edc_adherence.model_mixins import MedicationAdherenceModelMixin


class MedicationAdherence(
    MedicationAdherenceModelMixin, CrfModelMixin, edc_models.BaseUuidModel
):
    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Medication Adherence"
        verbose_name_plural = "Medication Adherence"
