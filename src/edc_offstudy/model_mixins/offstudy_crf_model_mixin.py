from django.db import models

from ..utils import raise_if_offstudy


class OffstudyCrfModelMixin(models.Model):

    """A mixin for CRF models to add the ability to determine
    if the subject is off study as of this CRFs report_datetime.

    CRFs by definition include CrfModelMixin in their declaration.
    See edc_visit_tracking.

    Also requires field "report_datetime"
    """

    def save(self, *args, **kwargs):
        raise_if_offstudy(
            subject_identifier=self.visit.subject_identifier,
            report_datetime=self.report_datetime,
            offstudy_model_cls=self.visit.visit_schedule.offstudy_model_cls,
        )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
