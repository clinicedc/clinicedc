from dateutil.relativedelta import relativedelta
from django.db import models

from ..refill import adjust_previous_end_datetime


class PreviousNextModelMixin(models.Model):
    @property
    def previous(self):
        return (
            self.__class__.objects.filter(refill_start_datetime__lt=self.refill_start_datetime)
            .order_by("refill_start_datetime")
            .last()
        )

    @property
    def next(self):
        return (
            self.__class__.objects.filter(refill_start_datetime__gt=self.refill_start_datetime)
            .order_by("refill_start_datetime")
            .first()
        )

    def adjust_end_datetimes(self):
        if self.previous:
            adjust_previous_end_datetime(
                self.previous,
                refill_start_datetime=self.refill_start_datetime,
                user_modified=self.user_modified,
                modified=self.modified,
            )
        if self.next:
            self.refill_end_datetime = self.next.refill_start_datetime - relativedelta(
                minutes=1
            )

    class Meta:
        abstract = True
