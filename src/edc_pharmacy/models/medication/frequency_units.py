from edc_list_data.model_mixins import ListModelMixin


class FrequencyUnits(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Frequency units"
        verbose_name_plural = "Frequency units"
