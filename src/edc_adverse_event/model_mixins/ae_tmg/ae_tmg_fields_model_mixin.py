from django.db import models
from django.utils import timezone

from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model.validators import datetime_not_future
from edc_model_fields.fields import OtherCharField

from ...models import AeClassification
from ...utils import get_adverse_event_app_label


def get_investigator_ae_classification_choices():
    choices = [(obj.name, obj.display_name) for obj in AeClassification.objects.all()]
    choices.append((NOT_APPLICABLE, "Not applicable"))
    return tuple(choices)


class AeTmgFieldsModelMixin(models.Model):
    ae_initial = models.ForeignKey(
        f"{get_adverse_event_app_label()}.aeinitial", on_delete=models.PROTECT
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time",
        validators=[datetime_not_future],
        default=timezone.now,
    )

    ae_received_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name="Date and time AE form received:",
    )

    clinical_review_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name="Date and time of clinical review: ",
    )

    ae_description = models.TextField(
        verbose_name="Description of AE:",
        default="",
        blank=True,
    )

    investigator_comments = models.TextField(
        verbose_name="This investigator's comments:",
        default="",
        blank=True,
    )

    ae_classification = models.CharField(max_length=150, blank=True, default="")

    ae_classification_other = OtherCharField(max_length=250, blank=True, default="")

    original_report_agreed = models.CharField(
        verbose_name="Does this investigator agree with the original AE report?",
        max_length=15,
        choices=YES_NO,
        default="",
        help_text="If No, explain in the narrative below",
    )

    investigator_narrative = models.TextField(verbose_name="Narrative", blank=True, default="")

    investigator_ae_classification_agreed = models.CharField(
        verbose_name=(
            "Does this investigator agree with the AE classification on the "
            "original AE report?"
        ),
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="If No, select a classification below",
    )

    investigator_ae_classification = models.ForeignKey(
        AeClassification,
        on_delete=models.PROTECT,
        verbose_name="Adverse Event (AE) Classification",
        null=True,
        help_text=(
            "Only applicable if this investigator does not agree with the original AE report"
        ),
    )

    investigator_ae_classification_other = OtherCharField(
        max_length=250, blank=True, default=""
    )

    officials_notified = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name="Date and time regulatory authorities notified (SUSARs)",
    )

    class Meta:
        abstract = True
