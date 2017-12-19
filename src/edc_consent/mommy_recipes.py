from edc_base.utils import get_utcnow
from edc_constants.constants import YES, MALE, NO
from faker import Faker
from model_mommy.recipe import Recipe, seq

from .models import SubjectConsent
from .tests import EdcConsentProvider

fake = Faker()
fake.add_provider(EdcConsentProvider)

subjectconsent = Recipe(
    SubjectConsent,
    consent_datetime=get_utcnow,
    dob=fake.dob_for_consenting_adult,
    first_name=fake.first_name,
    last_name=fake.last_name,
    # note, passes for model but won't pass validation in modelform clean()
    initials=fake.initials,
    gender=MALE,
    # will raise IntegrityError if multiple made without _quantity
    identity=seq('12315678'),
    # will raise IntegrityError if multiple made without _quantity
    confirm_identity=seq('12315678'),
    identity_type='OMANG',
    is_dob_estimated='-',
    language='en',
    is_literate=YES,
    is_incarcerated=NO,
    study_questions=YES,
    consent_reviewed=YES,
    consent_copy=YES,
    assessment_score=YES,
    consent_signature=YES,
    study_site='40',
)
