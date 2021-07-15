from edc_list_data.model_mixins import ListModelMixin


class ReasonsForTesting(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Reasons for Testing"
        verbose_name_plural = "Reasons for Testing"


class DiagnosisLocations(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Diagnosis Locations"
        verbose_name_plural = "Diagnosis Locations"
