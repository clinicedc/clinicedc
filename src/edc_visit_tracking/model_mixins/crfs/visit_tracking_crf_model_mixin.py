from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.deletion import PROTECT
from edc_model.models import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import SubjectScheduleModelMixin

from ...crf_date_validator import CrfDateValidator
from ...managers import CrfModelManager

from ..visit_model_mixin import VisitModelMixin


class VisitMethodsModelMixin(models.Model):
    """A model mixin for CRFs and Requisitions"""

    @property
    def visit_code(self):
        return self.subject_visit.visit_code

    @property
    def visit(self):
        """Returns the model instance of the visit foreign key
        attribute.
        """
        visit = None
        fields = {field.name: field for field in self._meta.fields}
        for name, field in fields.items():
            try:
                assert field.related_model is not None
            except (AttributeError, AssertionError):
                pass
            else:
                if issubclass(field.related_model, (VisitModelMixin,)):
                    try:
                        visit = getattr(self, name)
                    except ObjectDoesNotExist:
                        pass
        return visit

    @classmethod
    def visit_model_attr(cls):
        """Returns the field name for the visit model
        foreign key.
        """
        visit_model_attr = None
        fields = {field.name: field for field in cls._meta.fields}
        for name, field in fields.items():
            try:
                assert field.related_model is not None
            except (AttributeError, AssertionError):
                pass
            else:
                if issubclass(field.related_model, (VisitModelMixin,)):
                    visit_model_attr = name
        return visit_model_attr

    @classmethod
    def visit_model(cls):
        """Returns the visit foreign key model in
        label_lower format.
        """
        return cls.visit_model_cls()._meta.label_lower

    @classmethod
    def visit_model_cls(cls):
        """Returns the visit foreign key attribute model class.
        """
        fields = {field.name: field for field in cls._meta.fields}
        for name, field in fields.items():
            if name == cls.visit_model_attr():
                return field.related_model
        return None

    class Meta:
        abstract = True


class VisitTrackingCrfModelMixin(
    VisitMethodsModelMixin, SubjectScheduleModelMixin, models.Model
):
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
        return str(self.subject_visit)

    def natural_key(self):
        return (getattr(self, self.visit_model_attr()).natural_key(),)

    natural_key.dependencies = [settings.SUBJECT_VISIT_MODEL]

    @property
    def visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["subject_visit", "report_datetime"])]
