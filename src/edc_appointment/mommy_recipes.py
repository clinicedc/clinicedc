from faker import Faker
from model_mommy.recipe import Recipe, seq

from django.apps import apps as django_apps

from edc_base_test.faker import EdcBaseProvider

from .models import Appointment


def get_utcnow():
    return django_apps.get_app_config('edc_base_test').get_utcnow()

fake = Faker()
fake.add_provider(EdcBaseProvider)


appointment = Recipe(
    Appointment,
    appt_datetime=get_utcnow,
    timepoint=seq(0, increment_by=1),
    timepoint_datetime=get_utcnow,
    facility_name='clinic',
)
