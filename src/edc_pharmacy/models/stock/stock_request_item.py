from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_randomization.site_randomizers import site_randomizers
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.model_mixins import VisitCodeFieldsModelMixin

from ...exceptions import StockRequestItemError
from ..medication import Assignment
from ..prescription import Rx
from .stock_request import StockRequest


class Manager(models.Manager):
    use_in_migrations = True


class StockRequestItem(VisitCodeFieldsModelMixin, BaseUuidModel):
    """A model that represents a stock request item."""

    request_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    request_item_datetime = models.DateTimeField(default=timezone.now)

    stock_request = models.ForeignKey(
        StockRequest,
        verbose_name="Stock request",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    rx = models.ForeignKey(Rx, on_delete=models.PROTECT, null=True, blank=False)

    assignment = models.ForeignKey(Assignment, on_delete=models.PROTECT, null=True, blank=True)

    registered_subject = models.ForeignKey(
        RegisteredSubject,
        verbose_name="Subject",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    appt_datetime = models.DateTimeField(null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return (
            f"{self.registered_subject.subject_identifier}: {self.stock_request.formulation}"
        )

    def save(self, *args, **kwargs):
        """Important: check `bulk_create_stock_request_items`
        to ensure fields updated here are also manually
        updated when `bulk_update` is called.
        """
        if not self.request_item_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.request_item_identifier = f"{next_id:06d}"
        if not self.stock_request:
            raise StockRequestItemError("Stock request may not be null")
        if self.registered_subject.subject_identifier != self.rx.subject_identifier:
            raise StockRequestItemError(
                "Subject mismatch. Selected subject does not match prescription"
            )
        self.assignment = self.rx.get_assignment()
        super().save(*args, **kwargs)

    @classmethod
    def get_rando_sid(cls, randomizer_name: str, registered_subject: RegisteredSubject):
        randomizer = site_randomizers.get(randomizer_name)
        rando_obj = randomizer.model_cls().objects.get(
            subject_identifier=registered_subject.subject_identifier
        )
        return rando_obj.sid

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock request item"
        verbose_name_plural = "Stock request items"
