from edc_list_data.model_mixins import ListModelMixin


class RefusalReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Refusal Reason"
        verbose_name_plural = "Refusal Reasons"
