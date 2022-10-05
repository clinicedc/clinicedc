from __future__ import annotations

from typing import Any

from django.db import models

from ..utils import raise_if_offstudy


class OffstudyNonCrfModelError(Exception):
    pass


class OffstudyNonCrfModelMixin(models.Model):

    """Model mixin for non-CRF, PRN, visit, appt models.

    A mixin for non-CRF models to add the ability to determine
    if the subject is off study as of this non-CRFs report_datetime.

    Requires the fields `subject_identifier`, `report_datetime`.
    """

    def save(self: Any, *args, **kwargs):
        self.raise_if_offstudy()
        super().save(*args, **kwargs)

    def raise_if_offstudy(self) -> None:
        raise_if_offstudy(
            source_obj=self,
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
        )

    class Meta:
        abstract = True
