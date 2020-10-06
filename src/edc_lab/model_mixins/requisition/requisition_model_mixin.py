from django.conf import settings
from django.db import models
from django.utils import timezone
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_metadata.model_mixins.updates import UpdatesRequisitionMetadataModelMixin
from edc_model.models import HistoricalRecords
from edc_model.models import datetime_not_future
from edc_model.models import OtherCharField, InitialsField
from edc_protocol import Protocol
from edc_protocol.validators import datetime_not_before_study_start
from edc_reference.model_mixins import RequisitionReferenceModelMixin
from edc_search.model_mixins import SearchSlugModelMixin
from edc_sites.models import SiteModelMixin
from edc_visit_tracking.managers import CurrentSiteManager
from edc_visit_tracking.model_mixins import VisitTrackingCrfModelMixin
from edc_visit_tracking.model_mixins import PreviousVisitModelMixin

from ...choices import ITEM_TYPE, REASON_NOT_DRAWN
from ...managers import RequisitionManager
from ..panel_model_mixin import PanelModelMixin
from .requisition_verify_model_mixin import RequisitionVerifyModelMixin
from .requisition_status_mixin import RequisitionStatusMixin
from .requisition_identifier_mixin import RequisitionIdentifierMixin


class RequisitionModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    VisitTrackingCrfModelMixin,
    PanelModelMixin,
    PreviousVisitModelMixin,
    RequiresConsentFieldsModelMixin,
    RequisitionIdentifierMixin,
    RequisitionReferenceModelMixin,
    RequisitionStatusMixin,
    RequisitionVerifyModelMixin,
    SearchSlugModelMixin,
    SiteModelMixin,
    UpdatesRequisitionMetadataModelMixin,
    models.Model,
):
    requisition_datetime = models.DateTimeField(
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=timezone.now,
        verbose_name="Requisition Date",
    )

    drawn_datetime = models.DateTimeField(
        verbose_name="Date / Time Specimen Drawn",
        validators=[datetime_not_before_study_start, datetime_not_future],
        null=True,
        blank=True,
        help_text=("If not drawn, leave blank."),
    )

    is_drawn = models.CharField(
        verbose_name="Was a specimen drawn?",
        max_length=3,
        choices=YES_NO,
        help_text="If No, provide a reason below",
    )

    reason_not_drawn = models.CharField(
        verbose_name="If not drawn, please explain",
        max_length=25,
        default=NOT_APPLICABLE,
        choices=REASON_NOT_DRAWN,
    )

    reason_not_drawn_other = OtherCharField()

    protocol_number = models.CharField(max_length=10, null=True, editable=False)

    clinician_initials = InitialsField(null=True, blank=True)

    specimen_type = models.CharField(
        verbose_name="Specimen type", max_length=25, null=True, blank=True
    )

    item_type = models.CharField(
        verbose_name="Item collection type",
        max_length=25,
        choices=ITEM_TYPE,
        default=NOT_APPLICABLE,
        help_text="",
    )

    item_count = models.IntegerField(
        verbose_name="Number of items",
        null=True,
        blank=True,
        help_text=(
            "Number of tubes, samples, cards, etc being sent for this test/order only. "
            "Determines number of labels to print"
        ),
    )

    estimated_volume = models.DecimalField(
        verbose_name="Estimated volume in mL",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "If applicable, estimated volume of sample for this test/order. "
            'This is the total volume if number of "tubes" above is greater than 1'
        ),
    )

    comments = models.TextField(max_length=25, null=True, blank=True)

    on_site = CurrentSiteManager()

    objects = RequisitionManager()

    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return f"{self.panel_object.verbose_name}: {self.requisition_identifier}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.protocol_number = Protocol().protocol_number
        self.subject_identifier = self.subject_visit.subject_identifier
        self.specimen_type = self.panel_object.aliquot_type.alpha_code
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.requisition_identifier,)

    natural_key.dependencies = [settings.SUBJECT_VISIT_MODEL, "sites.Site"]

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.extend(
            [
                "subject_identifier",
                "requisition_identifier",
                "human_readable_identifier",
                "identifier_prefix",
            ]
        )
        return fields

    class Meta:
        abstract = True
        unique_together = ("panel", "subject_visit")
