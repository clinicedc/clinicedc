from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_model.models import BaseUuidModel
from edc_model_fields.fields import OtherCharField
from edc_utils import get_utcnow


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class HealthFacilityModelMixin(models.Model):
    """
    Note: Not yet integrated with the Facility object defined on
    visit objects and used to create appointments from the
    visit schedule.

    See also edc_appointment and edc_next_appointment.
    """

    report_datetime = models.DateTimeField(default=get_utcnow)

    name = models.CharField(max_length=25, unique=True)

    health_facility_type = models.ForeignKey(
        "edc_facility.HealthFacilityTypes",
        verbose_name="Health facility type",
        on_delete=models.PROTECT,
        related_name="+",
    )

    health_facility_type_other = OtherCharField()

    gps = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="copy and paste directly from google maps",
    )

    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        null=True,
        blank=True,
        help_text="in degrees. copy and paste directly from google maps",
    )

    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        null=True,
        blank=True,
        help_text="in degrees. copy and paste directly from google maps",
    )

    mon = models.BooleanField()
    tue = models.BooleanField()
    wed = models.BooleanField()
    thu = models.BooleanField()
    fri = models.BooleanField()
    sat = models.BooleanField()
    sun = models.BooleanField()

    notes = models.TextField(null=True, blank=True)

    objects = Manager()

    def __str__(self):
        return f"{self.name} {self.health_facility_type.display_name} {self.clinic_days_str}"

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.name,)

    @property
    def clinic_days(self) -> list[int]:
        """Using ISO numbering where Monday=1."""
        days = []
        if self.mon:
            days.append(1)
        if self.tue:
            days.append(2)
        if self.wed:
            days.append(3)
        if self.thu:
            days.append(4)
        if self.fri:
            days.append(5)
        if self.sat:
            days.append(6)
        if self.sun:
            days.append(7)
        return days

    @property
    def clinic_days_str(self) -> str:
        days = []
        mapping = {1: "M", 2: "T", 3: "W", 4: "Th", 5: "F", 6: "S", 7: "Su"}
        for day_int in self.clinic_days:
            days.append(mapping.get(day_int))
        return "".join(days)

    class Meta(BaseUuidModel.Meta):
        abstract = True
        verbose_name = "Health Facility"
        verbose_name_plural = "Health Facilities"
