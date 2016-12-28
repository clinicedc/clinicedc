from faker import Faker
from model_mommy.recipe import Recipe

from django.apps import apps as django_apps

from edc_base_test.faker import EdcBaseProvider

from .models import RegisteredSubject


def get_utcnow():
    return django_apps.get_app_config('edc_base_test').get_utcnow()

fake = Faker()
fake.add_provider(EdcBaseProvider)


registeredsubject = Recipe(
    RegisteredSubject,
    first_name=fake.first_name,
    last_name=fake.last_name,
)
