from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from clinicedc_constants import FEMALE
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import timezone
from model_bakery import baker

from edc_consent.utils import get_consent_model_name

if TYPE_CHECKING:
    from clinicedc_tests.models import SubjectScreening


class ConsentTestCaseMixin:
    @staticmethod
    def get_subject_consent(
        subject_screening: SubjectScreening | None = None,
        consent_datetime: datetime | None = None,
        site_id: int | None = None,
        dob: date | None = None,
        screening_identifier: str | None = None,
        gender: str | None = None,
        initials: str | None = None,
        age_in_years: int | None = None,
        report_datetime: datetime | None = None,
    ):
        now = timezone.now()
        now_as_date = timezone.now().date()
        screening_identifier = getattr(
            subject_screening,
            "screening_identifier",
            screening_identifier or "ABCDEF",
        )
        initials = getattr(subject_screening, "initials", initials or "XX")
        gender = getattr(subject_screening, "gender", gender or FEMALE)
        age_in_years = getattr(subject_screening, "age_in_years", age_in_years or 25)
        dob = dob or (now_as_date - relativedelta(years=age_in_years))
        report_datetime = getattr(subject_screening, "report_datetime", report_datetime or now)
        consent_datetime = consent_datetime or report_datetime

        return baker.make_recipe(
            get_consent_model_name(),
            user_created="erikvw",
            user_modified="erikvw",
            screening_identifier=screening_identifier,
            initials=initials,
            gender=gender,
            dob=dob,
            site=Site.objects.get(id=site_id or settings.SITE_ID),
            consent_datetime=consent_datetime,
        )
