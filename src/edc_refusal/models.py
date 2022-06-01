from django.db import models
from edc_list_data.model_mixins import ListModelMixin
from edc_model.models import BaseUuidModel, OtherCharField
from edc_model.models.historical_records import HistoricalRecords
from edc_search.model_mixins import SearchSlugManager
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow


class SubjectRefusalManager(SearchSlugManager, models.Manager):
    def get_by_natural_key(self, screening_identifier):
        return self.get(screening_identifier=screening_identifier)


class RefusalReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Refusal Reason"
        verbose_name_plural = "Refusal Reasons"


class SubjectRefusalModelMixin(models.Model):

    screening_identifier = models.CharField(max_length=50, unique=True)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    reason = models.ForeignKey(
        RefusalReasons,
        on_delete=models.PROTECT,
        verbose_name="Reason for refusal to join",
    )

    other_reason = OtherCharField()

    comment = models.TextField(
        verbose_name="Additional Comments",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.screening_identifier

    def natural_key(self):
        return (self.screening_identifier,)  # noqa

    @staticmethod
    def get_search_slug_fields():
        return ["screening_identifier"]

    class Meta:
        abstract = True


class SubjectRefusal(SubjectRefusalModelMixin, SiteModelMixin, BaseUuidModel):
    on_site = CurrentSiteManager()

    objects = SubjectRefusalManager()

    history = HistoricalRecords()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Subject Refusal"
        verbose_name_plural = "Subject Refusals"
