from edc_list_data.model_mixins import ListModelMixin


class VisitReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Visit Reasons"
        verbose_name_plural = "Visit Reasons"
