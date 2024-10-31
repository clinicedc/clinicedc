from edc_list_data.model_mixins import ListModelMixin


class FormulationType(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Formulation yype"
        verbose_name_plural = "Formulation types"
