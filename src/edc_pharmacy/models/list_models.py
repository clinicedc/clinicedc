from edc_list_data.model_mixins import ListModelMixin


class Container(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Container"
        verbose_name_plural = "Containers"


class FormulationType(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "FormulationType"
        verbose_name_plural = "FormulationTypes"


class FrequencyUnits(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Frequency units"
        verbose_name_plural = "Frequency units"


class Route(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Route"
        verbose_name_plural = "Routes"


class Units(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Units"
        verbose_name_plural = "Units"
