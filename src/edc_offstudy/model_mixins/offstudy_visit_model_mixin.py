from django.db import models

from ..utils import raise_if_offstudy


class OffstudyVisitModelMixin(models.Model):
    def save(self, *args, **kwargs):
        raise_if_offstudy(
            source_obj=self,
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            visit_schedule_name=self.visit_schedule_name,
        )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
