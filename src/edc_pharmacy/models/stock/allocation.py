from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_randomization.site_randomizers import site_randomizers
from edc_registration.models import RegisteredSubject

from ...exceptions import AllocationError
from .. import Assignment, Rx
from .stock_request_item import StockRequestItem


class Manager(models.Manager):
    use_in_migrations = True


class Allocation(BaseUuidModel):
    """A model to track stock allocation to a subject referring to a
    stock request.
    """

    allocation_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    allocation_datetime = models.DateTimeField(default=timezone.now)

    registered_subject = models.ForeignKey(
        RegisteredSubject,
        verbose_name="Allocated to",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    assignment = models.ForeignKey(Assignment, on_delete=models.PROTECT, null=True, blank=True)

    stock_request_item = models.OneToOneField(
        StockRequestItem,
        verbose_name="Requested",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    allocated_by = models.CharField(max_length=50, default="", blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.allocation_identifier

    def save(self, *args, **kwargs):
        if not self.allocation_identifier:
            self.allocation_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if not self.stock_request_item:
            raise AllocationError("Stock request item may not be null")
        self.assignment = self.get_assignment()
        super().save(*args, **kwargs)

    def get_assignment(self) -> Assignment:
        rx = Rx.objects.get(
            registered_subject=RegisteredSubject.objects.get(id=self.registered_subject.id)
        )
        randomizer = site_randomizers.get(rx.randomizer_name)
        assignment = randomizer.get_assignment(self.registered_subject.subject_identifier)
        return Assignment.objects.get(name=assignment)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Allocation"
        verbose_name_plural = "Allocations"
