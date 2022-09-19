from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import CrfScheduleModelMixin

from ...exceptions import RelatedVisitFieldError
from ...managers import CrfModelManager
from ..utils import get_related_visit_model_attr
from ..visit_model_mixin import VisitModelMixin

if TYPE_CHECKING:
    from edc_crf.stubs import CrfModelStub


class VisitMethodsModelMixin(models.Model):
    """A model mixin for CRFs and Requisitions"""

    @property
    def visit_code(self: CrfModelStub) -> str:
        return self.subject_visit.visit_code

    @classmethod
    def related_visit_model_attr(cls) -> str:
        """Returns the field name for the visit model foreign key."""
        return get_related_visit_model_attr(cls)

    @property
    def related_visit(self) -> VisitModelMixin:
        """Returns the model instance of the visit foreign key
        attribute.

        Note: doing this will cuase a RelatedObjectDoesNotExist exception:
            return getattr(self, self.related_visit_model_attr())
        RelatedObjectDoesNotExist cannot be imported since it is created
        at runtime.
        """
        related_visit = None
        for fld_cls in self._meta.get_fields():
            try:
                related_model = fld_cls.related_model
            except AttributeError:
                pass
            else:
                if related_model is not None and issubclass(related_model, (VisitModelMixin,)):
                    try:
                        related_visit = getattr(self, fld_cls.name)
                    except ObjectDoesNotExist:
                        pass
        return related_visit

    @classmethod
    def related_visit_field_cls(cls) -> Any | None:
        """Returns the field class of the visit foreign key attribute."""
        related_visit_field_cls = None
        for fld_cls in cls._meta.get_fields():
            if fld_cls.name == cls.related_visit_model_attr():
                related_visit_field_cls = fld_cls
                break
        if not related_visit_field_cls:
            raise RelatedVisitFieldError(f"Related visit field class not found. See {cls}.")
        return related_visit_field_cls

    @classmethod
    def related_visit_model_cls(cls) -> VisitModelMixin:
        """Returns the model class of the visit foreign key attribute."""
        related_model = None
        for fld_cls in cls._meta.get_fields():
            if fld_cls.name == cls.related_visit_model_attr():
                related_model = fld_cls.related_model
                break
        if not related_model:
            raise RelatedVisitFieldError(f"Related visit field class not found. See {cls}.")
        return related_model

    @classmethod
    def visit_model(cls) -> str:
        """Returns the name of the visit foreign key model in label_lower format"""
        return cls.related_visit_model_cls()._meta.label_lower

    class Meta:
        abstract = True


class VisitTrackingCrfModelMixin(VisitMethodsModelMixin, CrfScheduleModelMixin, models.Model):
    """Base mixin for all CRF models (used by edc-crf CrfModelMixin).

    CRFs have a OneToOne relation to the related visit model
    (Requisitions require one-to-many).

    Assumes `subject_visit` is the related visit model field attr
    on the Index.

    See also: edc_crf CrfModelMixin, RequisitionModelMixin
    """

    # assuming subject_visit
    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL, on_delete=models.PROTECT
    )

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

    def __str__(self) -> str:
        return str(self.related_visit)

    def natural_key(self) -> tuple:
        return (getattr(self, self.related_visit_model_attr()).natural_key(),)  # noqa

    # noinspection PyTypeHints
    natural_key.dependencies = [settings.SUBJECT_VISIT_MODEL]  # type:ignore

    @classmethod
    def related_visit_model_attr(cls) -> str:
        # assuming subject_visit
        return "subject_visit"

    @property
    def subject_identifier(self):
        return self.related_visit.subject_identifier

    class Meta:
        abstract = True
        # TODO: can this be add later? in metaclass? assumes attrname is subject_visit
        # assuming subject_visit
        indexes = [models.Index(fields=["subject_visit", "report_datetime"])]
