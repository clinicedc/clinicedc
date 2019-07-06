from django.db import models

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_visit_schedule.model_mixins import VisitScheduleMethodsModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleFieldsModelMixin

from ..choices import ENTRY_STATUS, REQUIRED, NOT_REQUIRED


class ModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    VisitScheduleMethodsModelMixin,
    VisitScheduleFieldsModelMixin,
    models.Model,
):

    """ Mixin for CrfMetadata and RequisitionMetadata models.
    """

    visit_code = models.CharField(max_length=25)

    visit_code_sequence = models.IntegerField(default=0)

    timepoint = models.DecimalField(null=True, decimal_places=1, max_digits=6)

    model = models.CharField(max_length=50)

    current_entry_title = models.CharField(max_length=250, null=True)

    show_order = models.IntegerField()  # must always be provided!

    entry_status = models.CharField(
        max_length=25, choices=ENTRY_STATUS, default=REQUIRED, db_index=True
    )

    due_datetime = models.DateTimeField(null=True, blank=True)

    report_datetime = models.DateTimeField(null=True, blank=True)

    entry_comment = models.TextField(max_length=250, null=True, blank=True)

    close_datetime = models.DateTimeField(null=True, blank=True)

    fill_datetime = models.DateTimeField(null=True, blank=True)

    def natural_key(self):
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
            self.model,
        )

    def is_required(self):
        return self.entry_status != NOT_REQUIRED

    def is_not_required(self):
        return not self.is_required()

    class Meta:
        abstract = True
        ordering = ("show_order",)
