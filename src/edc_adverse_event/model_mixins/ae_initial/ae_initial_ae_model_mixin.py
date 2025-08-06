from django.db import models
from edc_constants.choices import YES_NO, YES_NO_UNKNOWN
from edc_model_fields.fields.other_charfield import OtherCharField

from edc_adverse_event.models import AeActionClassification


class AeInitialAeModelMixin(models.Model):
    ae_study_relation_possibility = models.CharField(
        verbose_name="Is the incident related to the patient involvement in the study?",
        max_length=10,
        choices=YES_NO_UNKNOWN,
    )

    ae_cause = models.CharField(
        verbose_name=(
            "Has a reason other than the specified study drug been "
            "identified as the cause of the event(s)?"
        ),
        choices=YES_NO,
        max_length=5,
    )

    ae_cause_other = OtherCharField(
        verbose_name='If "Yes", specify', max_length=250, blank=True, null=True
    )

    ae_treatment = models.TextField(verbose_name="Specify action taken for treatment of AE:")

    ae_action_classification = models.ForeignKey(
        AeActionClassification,
        on_delete=models.PROTECT,
        verbose_name="Classification of action taken",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
