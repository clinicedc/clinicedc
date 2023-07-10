from django.db import models
from django.db.models.deletion import PROTECT
from django.utils import timezone
from edc_constants.constants import OPEN, OTHER
from edc_model import models as edc_models
from edc_search.model_mixins import SearchSlugManager, SearchSlugModelMixin
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from ..constants import PACKED, SHIPPED, STORAGE, TESTING, VERIFIED
from ..identifiers import BoxIdentifier
from ..model_mixins import VerifyBoxModelMixin
from .box_type import BoxType

BOX_DIMENSIONS = (("8 x 8", "8 x 8"), ("9 x 9", "9 x 9"), ("10 x 10", "10 x 10"))

BOX_CATEGORY = ((TESTING, "Testing"), (STORAGE, "Storage"), (OTHER, "Other"))

STATUS = (
    (OPEN, "Open"),
    (VERIFIED, "Verified"),
    (PACKED, "Packed"),
    (SHIPPED, "Shipped"),
)

human_readable_pattern = "^[A-Z]{3}\-[0-9]{4}\-[0-9]{2}$"


class BoxIsFullError(Exception):
    pass


class BoxManager(SearchSlugManager, models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, box_identifier):
        return self.get(box_identifier=box_identifier)


class Box(SearchSlugModelMixin, VerifyBoxModelMixin, SiteModelMixin, edc_models.BaseUuidModel):
    search_slug_fields = ["box_identifier", "human_readable_identifier", "name"]

    box_identifier = models.CharField(max_length=25, editable=False, unique=True)

    name = models.CharField(max_length=25, null=True, blank=True)

    box_datetime = models.DateTimeField(default=timezone.now)

    box_type = models.ForeignKey(BoxType, on_delete=PROTECT)

    category = models.CharField(max_length=25, default=TESTING, choices=BOX_CATEGORY)

    category_other = models.CharField(max_length=25, null=True, blank=True)

    specimen_types = models.CharField(
        max_length=25,
        help_text=(
            "List of specimen types in this box. Use two-digit numeric "
            "codes separated by commas."
        ),
    )

    status = models.CharField(max_length=15, default=OPEN, choices=STATUS)

    accept_primary = models.BooleanField(
        default=False,
        help_text="Tick to allow 'primary' specimens to be added to this box",
    )

    comment = models.TextField(null=True, blank=True)

    objects = BoxManager()

    on_site = CurrentSiteManager()

    history = edc_models.HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.box_identifier:
            self.box_identifier = BoxIdentifier().identifier
        if not self.name:
            self.name = self.box_identifier
        if self.id:
            self.update_verified()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.box_identifier,)

    natural_key.dependencies = ["edc_lab.boxtype", "sites.Site"]

    @property
    def count(self):
        return self.boxitem_set.all().count()

    @property
    def items(self):
        return self.boxitem_set.all().order_by("position")

    @property
    def human_readable_identifier(self):
        x = self.box_identifier
        return "{}-{}-{}".format(x[0:4], x[4:8], x[8:12])

    @property
    def next_position(self):
        """Returns an integer or None."""
        last_obj = self.boxitem_set.all().order_by("position").last()
        if not last_obj:
            next_position = 1
        else:
            next_position = last_obj.position + 1
        if next_position > self.box_type.total:
            raise BoxIsFullError(
                f"Box is full. Box {self.human_readable_identifier} has "
                f"{self.box_type.total} specimens."
            )
        return next_position

    @property
    def max_position(self):
        return

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Box"
        ordering = ("-box_datetime",)
        verbose_name_plural = "Boxes"
