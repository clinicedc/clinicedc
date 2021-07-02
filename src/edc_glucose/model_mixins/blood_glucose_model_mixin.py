# from django.conf import settings
# from django.db import models
# from django.db.models import PROTECT
# from edc_constants.choices import FASTING_CHOICES, YES_NO, YES_NO_NA
# from edc_constants.constants import FASTING, NOT_APPLICABLE
# from edc_lab.choices import GLUCOSE_UNITS_NA, RESULT_QUANTIFIER_NA
# from edc_model.models import date_not_future, datetime_not_future
# from edc_reportable.choices import REPORTABLE
#
#
# class BloodGlucoseModelMixin(models.Model):
#
#     is_poc = models.CharField(
#         verbose_name="Was a point-of-care test used?",
#         max_length=15,
#         choices=YES_NO,
#         null=True,
#     )
#
#     # blood glucose
#     glucose_requisition = models.ForeignKey(
#         f"{settings.SUBJECT_APP_LABEL}.subjectrequisition",
#         on_delete=PROTECT,
#         related_name="bg",
#         verbose_name="Requisition",
#         null=True,
#         blank=True,
#         help_text="Start typing the requisition identifier or select one from this visit",
#     )
#
#     glucose_assay_datetime = models.DateTimeField(
#         verbose_name="Result Report Date and Time",
#         validators=[datetime_not_future],
#         null=True,
#         blank=True,
#     )
#
#     fasting = models.CharField(
#         verbose_name="Was this fasting or non-fasting?",
#         max_length=25,
#         choices=FASTING_CHOICES,
#         null=True,
#         blank=True,
#     )
#
#     glucose_date = models.DateField(
#         validators=[date_not_future],
#         null=True,
#         blank=True,
#     )
#
#     fasting = models.CharField(
#         verbose_name="Has the participant fasted?",
#         max_length=15,
#         choices=YES_NO_NA,
#         default=NOT_APPLICABLE,
#     )
#
#     glucose = models.DecimalField(
#         verbose_name="Glucose result",
#         max_digits=8,
#         decimal_places=2,
#         null=True,
#         blank=True,
#     )
#
#     glucose_quantifier = models.CharField(
#         max_length=10,
#         choices=RESULT_QUANTIFIER_NA,
#         default=NOT_APPLICABLE,
#     )
#
#     glucose_units = models.CharField(
#         verbose_name="Units (glucose)",
#         max_length=15,
#         choices=GLUCOSE_UNITS_NA,
#         default=NOT_APPLICABLE,
#     )
#
#     glucose_abnormal = models.CharField(
#         verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
#     )
#
#     glucose_reportable = models.CharField(
#         verbose_name="reportable",
#         choices=REPORTABLE,
#         max_length=25,
#         null=True,
#         blank=True,
#     )
#
#     def get_summary_options(self):
#         opts = super().get_summary_options()
#         fasting = True if self.fasting == FASTING else False
#         opts.update(fasting=fasting)
#         return opts
#
#     class Meta:
#         abstract = True
