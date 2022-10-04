from django.db import models

from ..utils import raise_if_offstudy


class OffstudyCrfModelMixin(models.Model):

    """Model mixin for CRF models.

    A mixin for CRF models to add the ability to determine
    if the subject is off study as of this CRFs report_datetime.

    CRFs by definition include CrfModelMixin in their declaration.
    See edc_visit_tracking.

    Also requires field "report_datetime"
    """

    def save(self, *args, **kwargs):
        self.raise_if_offstudy()
        super().save(*args, **kwargs)

    def raise_if_offstudy(self) -> None:
        if self.subject_identifier and self.report_datetime:
            raise_if_offstudy(
                source_obj=self,
                subject_identifier=self.subject_identifier,
                report_datetime=self.report_datetime,
            )

    class Meta:
        abstract = True
