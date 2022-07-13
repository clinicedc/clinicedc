from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED
from faker import Faker
from model_bakery.recipe import Recipe, seq

from .models import SubjectConsent, SubjectVisit

fake = Faker()

subjectvisit = Recipe(SubjectVisit, reason=SCHEDULED)

subjectconsent = Recipe(
    SubjectConsent,
    confirm_identity=seq("12315678"),
    consent_datetime=get_utcnow(),
    dob=get_utcnow() - relativedelta(years=25),
    first_name=fake.first_name,
    gender="M",
    identity=seq("12315678"),
    initials="XX",
    is_dob_estimated="-",
    last_name=fake.last_name,
    screening_identifier=None,
    site=Site.objects.get_current(),
    subject_identifier=None,
    user_created="erikvw",
    user_modified="erikvw",
)
