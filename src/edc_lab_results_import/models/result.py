from django.conf import settings
from django.db import models
from django.db.models import CASCADE

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel


class Result(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):
    screening_identifier = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Screening identifier resolved from name_id.",
    )

    visit_code = models.CharField(
        max_length=25,
        blank=True,
        default="",
        help_text="Visit code from the linked SubjectRequisition.",
    )

    visit_code_sequence = models.IntegerField(
        null=True,
        blank=True,
        help_text="Visit code sequence from the linked SubjectRequisition.",
    )

    subject_visit = models.ForeignKey(
        settings.SUBJECT_VISIT_MODEL,
        null=True,
        on_delete=CASCADE,
    )

    visit_datetime = models.DateTimeField(null=True, blank=True)

    requisition = models.ForeignKey(
        settings.SUBJECT_REQUISITION_MODEL,
        null=True,
        on_delete=CASCADE,
    )

    requisition_identifier = models.CharField(
        max_length=50,
        blank=True,
        default="",
        db_index=True,
    )

    requisition_datetime = models.DateTimeField(null=True, blank=True)

    laboratory = models.CharField(
        verbose_name="Laboratory",
        max_length=25,
        blank=True,
        default="",
        help_text="Laboratory identifier (e.g. MNH) from --laboratory flag.",
    )

    source_file = models.CharField(max_length=200, blank=True, default="")

    report_datetime = models.DateTimeField(null=True, blank=True)

    report_type = models.CharField(max_length=50, blank=True, default="")

    result_status = models.CharField(max_length=50, blank=True, default="")

    order_no = models.CharField(max_length=50, blank=True, default="")

    order_datetime = models.DateTimeField(null=True, blank=True)

    ordered_by = models.CharField(max_length=100, blank=True, default="")

    sample_no = models.CharField(max_length=50, blank=True, default="")

    result_no = models.CharField(max_length=50, blank=True, default="")

    result_datetime = models.DateTimeField(null=True, blank=True)

    name_id = models.CharField(
        verbose_name="Name/ID from PDF",
        max_length=50,
        blank=True,
        default="",
    )

    age = models.IntegerField(null=True, blank=True)

    sex = models.CharField(max_length=10, blank=True, default="")

    clinic_ward = models.CharField(max_length=100, blank=True, default="")

    specimen_collected_by = models.CharField(max_length=100, blank=True, default="")

    specimen_collected_datetime = models.DateTimeField(null=True, blank=True)

    specimen_received_by = models.CharField(max_length=100, blank=True, default="")

    specimen_received_datetime = models.DateTimeField(null=True, blank=True)

    sample_type = models.CharField(max_length=25, blank=True, default="")

    sample_condition = models.CharField(max_length=25, blank=True, default="")

    priority = models.CharField(max_length=25, blank=True, default="")

    reported_by = models.CharField(max_length=100, blank=True, default="")

    reported_datetime = models.DateTimeField(null=True, blank=True)

    verified_by = models.CharField(max_length=100, blank=True, default="")

    verified_datetime = models.DateTimeField(null=True, blank=True)

    panel_name = models.CharField(max_length=50, blank=True, default="")

    source_utestid = models.CharField(max_length=50, blank=True, default="")

    utestid = models.CharField(
        verbose_name="EDC utestid",
        max_length=25,
        blank=True,
        default="",
    )

    source_units = models.CharField(max_length=25, blank=True, default="")

    units = models.CharField(max_length=25, blank=True, default="")

    result_value = models.DecimalField(
        verbose_name="Result",
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
    )

    converted_result_value = models.DecimalField(
        verbose_name="Converted result",
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Value converted to units recognized by edc_reportable.",
    )

    converted_units = models.CharField(
        max_length=25,
        blank=True,
        default="",
        help_text="Target units after conversion.",
    )

    flag = models.CharField(max_length=10, blank=True, default="")

    reference_range_lower = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )

    reference_range_upper = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )

    transcribed_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set when this result has been transcribed onto a CRF.",
    )

    def __str__(self):
        return f"{self.result_no}: {self.utestid} {self.result_value} {self.units}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Result"
        verbose_name_plural = "Results"
        constraints = (
            models.UniqueConstraint(
                fields=[
                    "order_no",
                    "result_no",
                    "sample_no",
                    "result_status",
                    "source_utestid",
                    "utestid",
                    "result_datetime",
                    "name_id",
                ],
                name="unique_lab_result",
            ),
        )
