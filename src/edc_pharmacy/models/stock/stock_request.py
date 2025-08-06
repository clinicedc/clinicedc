from django.db import models
from edc_constants.constants import CANCELLED, CLOSED, OPEN
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import InvalidContainer, StockRequestError
from ..medication import Formulation
from .container import Container
from .location import Location


class Manager(models.Manager):
    use_in_migrations = True


class StockRequest(BaseUuidModel):
    """A model to represent a stock request for subject stock.

    A request originates from, or is linked to, the research site
    using the location.
    """

    request_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    request_datetime = models.DateTimeField(default=get_utcnow)

    start_datetime = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text=(
            "If provided, will not include appointments before this date. May be left blank"
        ),
    )

    cutoff_datetime = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text=(
            "If provided, will not include appointments after this date. May be left blank"
        ),
    )

    location = models.ForeignKey(
        Location,
        verbose_name="Requested from",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        limit_choices_to={"site_id__isnull": False},
    )

    formulation = models.ForeignKey(
        Formulation,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    container = models.ForeignKey(
        Container,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        limit_choices_to={"may_dispense_as": True},
    )

    containers_per_subject = models.PositiveSmallIntegerField(
        verbose_name="Number of containers per subject", default=3
    )

    item_count = models.IntegerField(
        verbose_name="Item count",
        default=0,
        help_text="Matches the number of Request items.",
    )

    subject_identifiers = models.TextField(
        verbose_name="Include ONLY these subjects in this request. (Usually left blank)",
        null=True,
        blank=True,
        help_text=(
            "By adding subject identifiers in this box, only these subjects "
            "will be included in the request. All others will be ignored."
        ),
    )

    excluded_subject_identifiers = models.TextField(
        verbose_name="Exclude these subjects from this request. (Usually left blank)",
        null=True,
        blank=True,
    )

    labels = models.TextField(
        verbose_name="Labels",
        null=True,
        blank=True,
        help_text=(
            "A cell to capture and confirm printed/scanned labels related to this "
            "Stock request. See StockRequestItem."
        ),
    )

    cancel = models.CharField(
        verbose_name="To cancel this request, type the word 'CANCEL' here and save the form:",
        max_length=6,
        default=None,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=25,
        choices=(
            (OPEN, OPEN.title()),
            (CLOSED, CLOSED.title()),
            (CANCELLED, CANCELLED.title()),
        ),
        default=OPEN,
    )

    task_id = models.UUIDField(null=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.request_identifier

    def save(self, *args, **kwargs):
        if not self.request_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.request_identifier = f"{next_id:06d}"
        if not self.container.may_request_as:
            raise InvalidContainer(
                "Invalid stock.container. Must be a `subject-specific` container. "
                "Perhaps catch this in the form."
            )
        if not self.formulation:
            raise StockRequestError("Formulation may not be null")

        if self.subject_identifiers:
            subject_identifiers = self.subject_identifiers.split("\n")
            subject_identifiers = [s.strip() for s in subject_identifiers]
            self.subject_identifiers = "\n".join(subject_identifiers)
            if RegisteredSubject.objects.values("subject_identifier").filter(
                subject_identifier__in=subject_identifiers
            ).count() != len(subject_identifiers):
                raise StockRequestError(
                    "Invalid subject_identifier listed. Perhaps catch this in the form"
                )

        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock request"
        verbose_name_plural = "Stock requests"
