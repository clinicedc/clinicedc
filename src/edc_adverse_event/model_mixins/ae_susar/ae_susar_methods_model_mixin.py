from django.db import models
from edc_constants.constants import CLOSED, OPEN


class AeSusarMethodsModelMixin(models.Model):
    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.ae_initial.subject_identifier
        if self.submitted_datetime:
            self.report_status = CLOSED
            self.report_closed_datetime = self.submitted_datetime
        else:
            self.report_status = OPEN
            self.report_closed_datetime = None
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier,)  # noqa

    class Meta:
        abstract = True
