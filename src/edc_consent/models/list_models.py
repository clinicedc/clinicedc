from edc_list_data.model_mixins import ListModelManager, ListModelMixin
from edc_model.models import HistoricalRecords


class CeasedConsentOptions(ListModelMixin):
    objects = ListModelManager()
    history = HistoricalRecords()

    class Meta(ListModelMixin.Meta):
        verbose_name = "Ceased consent option"
        verbose_name_plural = "Ceased consent option"


class RetainedConsentOptions(ListModelMixin):
    objects = ListModelManager()
    history = HistoricalRecords()

    class Meta(ListModelMixin.Meta):
        verbose_name = "Retained consent option"
        verbose_name_plural = "Retained consent option"
