from edc_list_data.model_mixins import ListModelMixin


class Formulation(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Formulation"
        verbose_name_plural = "Formulations"


class Units(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Units"
        verbose_name_plural = "Units"


class Route(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Route"
        verbose_name_plural = "Routes"


class FrequencyUnits(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Frequency units"
        verbose_name_plural = "Frequency units"
