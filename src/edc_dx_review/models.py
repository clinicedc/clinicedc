from edc_list_data.model_mixins import ListModelManager, ListModelMixin
from edc_model.models import HistoricalRecords


class ReasonsForTesting(ListModelMixin):
    objects = ListModelManager()
    history = HistoricalRecords()

    class Meta(ListModelMixin.Meta):
        verbose_name = "Reasons for Testing"
        verbose_name_plural = "Reasons for Testing"


class DiagnosisLocations(ListModelMixin):
    objects = ListModelManager()
    history = HistoricalRecords()

    class Meta(ListModelMixin.Meta):
        verbose_name = "Diagnosis Locations"
        verbose_name_plural = "Diagnosis Locations"
