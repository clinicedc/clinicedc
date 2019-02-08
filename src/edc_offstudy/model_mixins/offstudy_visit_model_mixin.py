from django.db import models

from ..utils import raise_if_offstudy


class OffstudyVisitModelMixin(models.Model):
    def save(self, *args, **kwargs):
        raise_if_offstudy(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            offstudy_model_cls=self.visit_schedule.offstudy_model_cls,
        )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
