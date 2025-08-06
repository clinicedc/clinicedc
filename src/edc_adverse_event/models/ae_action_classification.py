from edc_list_data.model_mixins import ListUuidModelMixin


class AeActionClassification(ListUuidModelMixin):
    """Classification of action taken"""

    class Meta(ListUuidModelMixin.Meta):
        pass
