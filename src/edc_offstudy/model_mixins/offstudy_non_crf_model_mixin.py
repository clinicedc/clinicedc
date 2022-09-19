from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import models

from ..utils import raise_if_offstudy


class OffstudyNonCrfModelError(Exception):
    pass


class OffstudyNonCrfModelMixin(models.Model):

    """Model mixin for non-CRF, PRN, visit, appt models.

    A mixin for non-CRF models to add the ability to determine
    if the subject is off study as of this non-CRFs report_datetime.

    Requires fields subject_identifier, report_datetime,
    visit_schedule_name. If visit_schedule_name is not on the model,
    use method offstudy_model_cls,
    """

    offstudy_model: str | None = getattr(settings, "EDC_OFFSTUDY_OFFSTUDY_MODEL", None)

    def save(self: Any, *args, **kwargs):
        raise_if_offstudy(
            source_obj=self,
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            offstudy_model=self.offstudy_model,
        )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
