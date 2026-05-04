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

    subject_identifier = models.CharField(
        max_length=50, default="", blank=True, editable=False
    )

    code = models.CharField(
        verbose_name="Stock code",
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        help_text="A unique alphanumeric code",
        editable=False,
    )

    # OneToOne → FK refactor fields.
    # `stock` was previously the reverse accessor of Stock.allocation (OneToOneField).
    # Now it is an explicit forward FK; Stock.allocation is the sticky cache pointer.
    # Change required so a stock item may be reallocated after being repooled.
    # Sticky-pointer policy (see DESIGN_transaction_log.md):
    #   * Stock.allocation is preserved across dispense, damage, destroy, expire,
    #     lose, void, quarantine — i.e. for the bottle's entire forward life.
    #   * It is cleared only on RETURN_DISPOSITION_REPOOLED, the one transaction
    #     that returns the bottle to the available pool.
    #   * Allocation.ended_datetime / Allocation.ended_reason are stamped on
    #     every "end" transaction regardless of whether Stock.allocation is cleared.
    # See also StockTransaction.from_allocation / to_allocation.
    stock = models.ForeignKey(
        "edc_pharmacy.stock",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="allocations",
        help_text="Stock item allocated to this subject.",
    )

    started_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the allocation became active (defaults to allocation_datetime).",
    )

    ended_datetime = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When the allocation ended (NULL = still active).",
    )

    ended_reason = models.CharField(
        max_length=50,
        default="",
        blank=True,
        help_text="Why the allocation ended (dispensed, returned, reallocated, …).",
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.allocation_identifier

    def save(self, *args, **kwargs):
        if not self.allocation_identifier:
            self.allocation_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if not self.stock_request_item:
            raise AllocationError("Stock request item may not be null")
        self.subject_identifier = self.registered_subject.subject_identifier
        self.assignment = self.get_assignment()
        if not self.started_datetime:
            self.started_datetime = self.allocation_datetime or timezone.now()
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
        constraints = [
            # At most one *active* (un-ended) Allocation per Stock.
            # Sticky-pointer policy (see DESIGN_transaction_log.md §5.6):
            # ended Allocation rows remain — many per stock — but only one
            # may have ended_datetime IS NULL at a time. Catches cache drift
            # between Stock.allocation and the canonical Allocation table at
            # write time rather than at audit time.
            models.UniqueConstraint(
                fields=["stock"],
                condition=models.Q(ended_datetime__isnull=True),
                name="one_active_allocation_per_stock",
            ),
        ]
