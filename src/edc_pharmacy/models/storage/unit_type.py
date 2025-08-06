from edc_list_data.model_mixins import ListModelMixin


class UnitType(ListModelMixin):
    """Unit type in a container.

    For example, `tablet`.
    """

    class Meta(ListModelMixin.Meta):
        pass
