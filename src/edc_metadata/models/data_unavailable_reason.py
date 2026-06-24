from edc_list_data.model_mixins import ListModelMixin


class DataUnavailableReason(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Data unavailable reason"
        verbose_name_plural = "Data unavailable reasons"
