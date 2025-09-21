from django.db import models
from django.utils import timezone

from edc_model.models import OtherCharField


class SubjectRefusalModelMixin(models.Model):
    screening_identifier = models.CharField(max_length=50, unique=True)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=timezone.now
    )

    reason = models.ForeignKey(
        "edc_refusal.RefusalReasons",
        on_delete=models.PROTECT,
        verbose_name="Reason for refusal to join",
    )

    other_reason = OtherCharField()

    comment = models.TextField(
        verbose_name="Additional Comments",
        default="",
        blank=True,
    )

    def __str__(self):
        return self.screening_identifier

    def natural_key(self):
        return (self.screening_identifier,)

    @staticmethod
    def get_search_slug_fields():
        return ("screening_identifier",)

    class Meta:
        abstract = True
