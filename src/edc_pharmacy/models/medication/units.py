from edc_list_data.model_mixins import ListModelMixin


class Units(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Units"
        verbose_name_plural = "Units"
