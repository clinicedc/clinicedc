from django.conf import settings
from django.db import models
from django.db.models.deletion import PROTECT
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import get_utcnow

from ...crf_date_validator import CrfDateValidator
from ...managers import CrfModelManager
from .crf_visit_methods_model_mixin import CrfVisitMethodsModelMixin


class CrfModelMixin(CrfVisitMethodsModelMixin, models.Model):

    """Base mixin for all CRF models.

    You need to define the visit model foreign_key, e.g:

        subject_visit = models.ForeignKey(SubjectVisit)

    and specify the `natural key` with its dependency of the visit model.
    """

    subject_visit = models.ForeignKey(settings.SUBJECT_VISIT_MODEL, on_delete=PROTECT)

    crf_date_validator_cls = CrfDateValidator

    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
        help_text=(
            "If reporting today, use today's date/time, otherwise use "
            "the date/time this information was reported."
        ),
    )

    objects = CrfModelManager()

    def __str__(self):
        return str(self.visit)

    def natural_key(self):
        return (getattr(self, self.visit_model_attr()).natural_key(),)

    natural_key.dependencies = [settings.SUBJECT_VISIT_MODEL]

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["subject_visit", "report_datetime"])]
