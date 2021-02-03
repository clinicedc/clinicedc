from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_constants.constants import MALE, NO, YES
from edc_utils import get_utcnow
from faker import Faker
from model_bakery.recipe import Recipe, seq

from .tests.models import SubjectConsent

fake = Faker()

subjectconsent = Recipe(
    SubjectConsent,
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
