from edc_list_data.model_mixins import ListModelMixin


class Route(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Route"
        verbose_name_plural = "Routes"
