from faker import Faker
from model_mommy.recipe import Recipe

from edc_base_test.faker import EdcBaseProvider

from .models import RegisteredSubject


fake = Faker()
fake.add_provider(EdcBaseProvider)


registeredsubject = Recipe(
    RegisteredSubject,
    subject_identifier=None,
    subject_identifier_as_pk=None,
    first_name=fake.first_name,
    last_name=fake.last_name,
    study_site='40',
)
