from faker import Faker
from model_mommy.recipe import Recipe, seq

from edc_base_test.faker import EdcBaseProvider
from edc_base_test.utils import get_utcnow

from .models import Appointment


fake = Faker()
fake.add_provider(EdcBaseProvider)


appointment = Recipe(
    Appointment,
    appt_datetime=get_utcnow,
    timepoint=seq(0, increment_by=1),
    timepoint_datetime=get_utcnow,
    facility_name='clinic',
)
