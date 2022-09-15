from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import PROTECT
from edc_action_item.models import ActionModelMixin
from edc_constants.constants import NEW
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model import models as edc_models
from edc_randomization.site_randomizers import site_randomizers
from edc_registration.models import RegisteredSubject
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import formatted_age, get_utcnow

from ..choices import PRESCRIPTION_STATUS
from ..constants import PRESCRIPTION_ACTION
from ..exceptions import PrescriptionError
from .medication import Medication
from .search_slug_model_mixin import SearchSlugModelMixin
from .subject import Subject


class Rx(
    NonUniqueSubjectIdentifierFieldMixin,
    SiteModelMixin,
    ActionModelMixin,
    SearchSlugModelMixin,
    edc_models.BaseUuidModel,
):

    """A model for the prescription.

    In this context the `prescription` specifies only the medication.
    The formulation and dosage guidelines are specified
    on each Refill.
    """

    action_name = PRESCRIPTION_ACTION

    rx_identifier = models.CharField(max_length=36, default=uuid4)

    rx_name = models.CharField(max_length=36, default="study prescription")

    registered_subject = models.ForeignKey(
        Subject,
        verbose_name="Subject Identifier",
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    report_datetime = models.DateTimeField(default=get_utcnow)

    rx_date = models.DateField(verbose_name="Date RX written", default=get_utcnow)

    rx_expiration_date = models.DateField(
        verbose_name="Date RX expires",
        null=True,
        blank=True,
        help_text="Leave blank. Will be filled when end of study report is submitted",
    )

    status = models.CharField(max_length=25, default=NEW, choices=PRESCRIPTION_STATUS)

    medications = models.ManyToManyField(Medication, blank=False)

    refill = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of times this prescription may be refilled",
    )

    rando_sid = models.CharField(max_length=25, null=True, blank=True)

    randomizer_name = models.CharField(max_length=25, null=True, blank=True)

    weight_in_kgs = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)

    clinician_initials = models.CharField(max_length=3, null=True)

    notes = models.TextField(
        max_length=250,
        null=True,
        blank=True,
        help_text="Private notes for pharmacist only",
    )

    on_site = CurrentSiteManager()

    def __str__(self):
        return f"{self.subject_identifier}"

    def natural_key(self):
        return (self.rx_identifier,)  # noqa

    def save(self, *args, **kwargs):
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=self.subject_identifier
        )
        if self.randomizer_name:
            randomizer = site_randomizers.get(self.randomizer_name)
            try:
                self.rando_sid = (
                    randomizer.model_cls()
                    .objects.get(subject_identifier=self.subject_identifier)
                    .sid
                )
            except ObjectDoesNotExist:
                raise PrescriptionError(
                    "Unable to create prescription. Subject has not been "
                    f"randomized (randomizer={self.randomizer_name}"
                )
        super().save(*args, **kwargs)

    def description(self):
        return (
            f"{','.join([o.display_name for o in self.medications.all()])} "
            f"{self.registered_subject.subject_identifier} {self.registered_subject.initials} "
            f"{formatted_age(born=self.registered_subject.dob, reference_dt=get_utcnow())} "
            f"{self.registered_subject.gender} "
            f"Written: {self.rx_date}"
        )

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"
