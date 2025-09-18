from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from edc_model.models import BaseUuidModel
from edc_registration.models import RegisteredSubject

from ..exceptions import ValueBoundryError
from ..utils import get_grade_for_value, get_normal_data_or_raise
from .grading_exception import GradingException

if TYPE_CHECKING:
    from .grading_data import GradingData
    from .normal_data import NormalData


class ReferenceRangeCollection(BaseUuidModel):
    name = models.CharField(max_length=50, unique=True)

    grade1 = models.BooleanField(default=False)
    grade2 = models.BooleanField(default=False)
    grade3 = models.BooleanField(default=True)
    grade4 = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def grades(self, label: str) -> list[int]:
        return self.reportable_grades(label)

    def default_grades(self) -> list[int]:
        """Default grades considered for this collection.

        See also model GradingException.
        """
        grades = []
        for i in range(1, 5):
            if getattr(self, f"grade{i}"):
                grades.append(i)
        return grades

    def reportable_grades(self, label: str) -> list[int]:
        if not label:
            raise ValueError("Unable to determine reportable grades. Label may not be None")
        try:
            grading_exception = GradingException.objects.get(
                reference_range_collection=self, label=label
            )
        except ObjectDoesNotExist:
            reportable_grades = self.default_grades()
        else:
            reportable_grades = grading_exception.grades
        return reportable_grades

    def get_grade(
        self,
        value: float | int | None = None,
        label: str | None = None,
        units: str | None = None,
        subject_identifier: str | None = None,
        report_datetime: datetime | None = None,
        gender: str | None = None,
        dob: date | None = None,
        age_units: str | None = None,
        site: Site | None = None,
    ) -> tuple[GradingData | None, str | None]:
        if subject_identifier:
            rs_obj = RegisteredSubject.objects.get(subject_identifier=subject_identifier)
            dob = rs_obj.dob
            gender = rs_obj.gender
        grading_data, eval_phrase = get_grade_for_value(
            reference_range_collection=self,
            value=value,
            label=label,
            units=units,
            gender=gender,
            dob=dob,
            report_datetime=report_datetime,
            age_units=age_units,
            site=site,
        )
        return grading_data, eval_phrase

    def is_normal(
        self,
        value: float | int | None = None,
        label: str | None = None,
        units: str | None = None,
        subject_identifier: str | None = None,
        report_datetime: datetime | None = None,
        gender: str | None = None,
        dob: date | None = None,
        age_units: str | None = None,
        site: Site | None = None,
    ) -> tuple[bool, NormalData]:
        if subject_identifier:
            rs_obj = RegisteredSubject.objects.get(subject_identifier=subject_identifier)
            dob = rs_obj.dob
            gender = rs_obj.gender
        normal_data = get_normal_data_or_raise(
            reference_range_collection=self,
            label=label,
            units=units,
            gender=gender,
            dob=dob,
            report_datetime=report_datetime,
            age_units=age_units,
        )
        try:
            is_normal = normal_data.value_in_normal_range_or_raise(
                value=value,
                dob=dob,
                report_datetime=report_datetime,
                age_units=age_units,
            )
        except ValueBoundryError:
            is_normal = False
        return is_normal, normal_data

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Reference Range Collection"
        verbose_name_plural = "Reference Range Collections"
