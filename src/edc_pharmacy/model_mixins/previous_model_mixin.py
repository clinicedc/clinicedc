from dateutil.relativedelta import relativedelta
from django.db import models

from ..exceptions import RefillEndDatetimeError
from ..refill import adjust_previous_end_datetime


class PreviousNextModelMixin(models.Model):
    def update_or_raise_on_null_refill_end_datetimes(self):
        if self.__class__.objects.filter(refill_end_datetime__isnull=True).exists():
            obj = (
                self.__class__.objects.filter(refill_end_datetime__isnull=True)
                .exclude(id=self.id)
                .order_by("refill_start_datetime")
                .first()
            )
            raise RefillEndDatetimeError(
                f"refill_end_datetime cannot be null. See {obj.__class__.__name__}({obj})."
            )

    @property
    def previous(self):
        # self.update_or_raise_on_null_refill_end_datetimes()
        opts = {"refill_start_datetime__lt": self.refill_start_datetime}
        if getattr(self, "related_visit_model_attr", None):
            opts.update(
                {
                    f"{self.related_visit_model_attr()}__subject_identifier": (
                        self.related_visit.subject_identifier
                    )
                }
            )
        else:
            opts.update({"rx__subject_identifier": self.rx.subject_identifier})
        return (
            self.__class__.objects.filter(**opts)
            .order_by("refill_start_datetime")
            .exclude(refill_identifier=self.refill_identifier)
            .last()
        )

    @property
    def next(self):
        # self.update_or_raise_on_null_refill_end_datetimes()
        opts = {"refill_start_datetime__gt": self.refill_start_datetime}
        if getattr(self, "related_visit_model_attr", None):
            opts.update(
                {
                    f"{self.related_visit_model_attr()}__subject_identifier": (
                        self.related_visit.subject_identifier
                    )
                }
            )
        else:
            opts.update({"rx__subject_identifier": self.rx.subject_identifier})
        return (
            self.__class__.objects.filter(**opts)
            .order_by("refill_start_datetime")
            .exclude(refill_identifier=self.refill_identifier)
            .first()
        )

    def adjust_end_datetimes(self):
        """Adjust the refill_end_datetime for the previous and
        next instance.

        For example: study medication or rxrefill model instance.
        """
        if self.previous:  # e.g. prev study_med or rx_refill
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
