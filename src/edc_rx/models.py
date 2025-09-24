from edc_list_data.model_mixins import ListModelMixin


class RxModificationReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Treatment Modification Reasons"
        verbose_name_plural = "Treatment Modification Reasons"


class RxModifications(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Treatment Modifications"
        verbose_name_plural = "Treatment Modifications"
