from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from faker import Faker
from model_bakery.recipe import Recipe, seq

from edc_constants.constants import GRADE4, MALE, NO, NOT_APPLICABLE, YES
from edc_utils import get_utcnow
from .models import (
    AeFollowup,
    AeInitial,
    AeSusar,
    AeTmg,
    DeathReport,
    DeathReportTmg,
    DeathReportTmgSecond,
    SubjectConsent,
    SubjectConsentV1,
    SubjectConsentV1Ext,
    SubjectConsentV2,
    SubjectConsentV3,
    SubjectConsentV4,
)

fake = Faker()


def get_consent_opts():
    return dict(
        consent_datetime=get_utcnow,
        dob=get_utcnow() - relativedelta(years=25),
        first_name=fake.first_name,
        last_name=fake.last_name,
        # note, passes for model but won't pass validation in modelform clean()
        initials="AA",
        gender=MALE,
        # will raise IntegrityError if multiple made without _quantity
        identity=seq("12315678"),
        # will raise IntegrityError if multiple made without _quantity
        confirm_identity=seq("12315678"),
        identity_type="passport",
        is_dob_estimated="-",
        language="en",
        is_literate=YES,
        is_incarcerated=NO,
        study_questions=YES,
        consent_reviewed=YES,
        consent_copy=YES,
        assessment_score=YES,
        consent_signature=YES,
        site=Site.objects.get_current(),
    )


subjectconsent = Recipe(SubjectConsent, **get_consent_opts())
subjectconsentv1 = Recipe(SubjectConsentV1, **get_consent_opts())
subjectconsentv2 = Recipe(SubjectConsentV2, **get_consent_opts())
subjectconsentv3 = Recipe(SubjectConsentV3, **get_consent_opts())
subjectconsentv4 = Recipe(SubjectConsentV4, **get_consent_opts())
subjectconsentv1ext = Recipe(SubjectConsentV1Ext, **get_consent_opts())


aeinitial = Recipe(
    AeInitial,
    report_datetime=get_utcnow() - relativedelta(days=5),
    action_identifier=None,
    ae_description="A description of this event",
    ae_grade=GRADE4,
    ae_study_relation_possibility=YES,
    ae_start_date=get_utcnow().date() + relativedelta(days=5),
    ae_awareness_date=get_utcnow().date() + relativedelta(days=5),
    sae=NO,
    susar=NO,
    susar_reported=NOT_APPLICABLE,
    ae_cause=NO,
    ae_cause_other=None,
)

aetmg = Recipe(
    AeTmg,
    action_identifier=None,
    report_datetime=get_utcnow(),
)

aesusar = Recipe(
    AeSusar,
    action_identifier=None,
    report_datetime=get_utcnow(),
)

aefollowup = Recipe(
    AeFollowup,
    relevant_history=NO,
    action_identifier=None,
    report_datetime=get_utcnow(),
)


deathreport = Recipe(
    DeathReport,
    action_identifier=None,
    report_datetime=get_utcnow(),
    death_datetime=get_utcnow(),
)


deathreporttmg = Recipe(
    DeathReportTmg,
    action_identifier=None,
    report_datetime=get_utcnow(),
)


deathreporttmgsecond = Recipe(
    DeathReportTmgSecond,
    action_identifier=None,
    report_datetime=get_utcnow(),
)
