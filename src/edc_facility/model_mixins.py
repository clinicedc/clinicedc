import calendar

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from edc_model.models import BaseUuidModel
from edc_model_fields.fields import OtherCharField


class HealthFacilityCalendarError(Exception):
    pass


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class HealthFacilityModelMixin(models.Model):
    """
    Note: Not yet integrated with the Facility object defined on
    visit objects and used to create appointments from the
    visit schedule.

    See also edc_appointment.
    """

    report_datetime = models.DateTimeField(default=timezone.now)

    name = models.CharField(max_length=25, unique=True)

    title = models.CharField(max_length=150, default="", blank=True)

    health_facility_type = models.ForeignKey(
        "edc_facility.HealthFacilityTypes",
        verbose_name="Health facility type",
        on_delete=models.PROTECT,
        related_name="+",
    )

    health_facility_type_other = OtherCharField()

    gps = models.CharField(
        max_length=50,
        default="",
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

    notes = models.TextField(default="", blank=True)

    objects = Manager()

    def __str__(self):
        return f"{self.name.upper()} {self.health_facility_type.display_name}"

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.name,)

    @property
    def clinic_days(self) -> list[int]:
        """Using non-ISO numbering where Monday=0."""
        if calendar.firstweekday() != 0:
            raise HealthFacilityCalendarError(
                f"Expected first day of week to be 0. Got {calendar.firstweekday()}."
            )
        days = []
        if self.mon:
            days.append(calendar.MONDAY)
        if self.tue:
            days.append(calendar.TUESDAY)
        if self.wed:
            days.append(calendar.WEDNESDAY)
        if self.thu:
            days.append(calendar.THURSDAY)
        if self.fri:
            days.append(calendar.FRIDAY)
        if self.sat:
            days.append(calendar.SATURDAY)
        if self.sun:
            days.append(calendar.SUNDAY)
        return days

    @property
    def clinic_days_str(self) -> str:
        days = []
        mapping = {k: v for k, v in enumerate(calendar.weekheader(3).split(" "))}
        for day_int in self.clinic_days:
            days.append(mapping.get(day_int))  # noqa: PERF401
        return ",".join(days)

    class Meta(BaseUuidModel.Meta):
        abstract = True
        verbose_name = "Health Facility"
        verbose_name_plural = "Health Facilities"
