from django.db import models

from edc_base.model.validators import date_not_before_study_start, date_not_future
from edc_constants.choices import YES_NO, ALIVE_DEAD_UNKNOWN
from edc_constants.constants import YES, ALIVE


class CaretakerFieldsMixin(models.Model):
    """A fields mixin for visit models where information on the the participant is offered by
    another person, as in the case of infant and mother.

    One the ModelForm, override the default form to customize the choices and labels.

    """
    information_provider = models.CharField(
        verbose_name="Please indicate who provided most of the information for this participant's visit",
        max_length=20)

    information_provider_other = models.CharField(
        verbose_name="if information provider is Other, please specify",
        max_length=20,
        blank=True,
        null=True)

    is_present = models.CharField(
        max_length=10,
        verbose_name="Is the participant present at today\'s visit",
        choices=YES_NO,
        default=YES)

    survival_status = models.CharField(
        max_length=10,
        verbose_name="Participant\'s survival status",
        choices=ALIVE_DEAD_UNKNOWN,
        null=True,
        default=ALIVE)

    last_alive_date = models.DateField(
        verbose_name="Date participant last known alive",
        validators=[date_not_before_study_start, date_not_future],
        null=True,
        blank=True)

    class Meta:
        abstract = True
