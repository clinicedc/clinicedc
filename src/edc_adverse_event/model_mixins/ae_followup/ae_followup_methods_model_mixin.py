from django.db import models
from edc_constants.constants import NOT_APPLICABLE


class AeFollowupMethodsModelMixin(models.Model):
    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.ae_initial.subject_identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier,)

    @property
    def report_date(self):
        """Returns a date based on the UTC datetime."""
        return self.report_datetime.date()

    @property
    def severity(self):
        if self.ae_grade == NOT_APPLICABLE:
            return "unchanged"
        return self.ae_grade

    def get_action_item_reason(self):
        return self.ae_initial.ae_description

    class Meta:
        abstract = True
