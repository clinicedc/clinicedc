from dateutil.relativedelta import relativedelta
from edc_base.utils import get_utcnow
from edc_consent.tests import EdcConsentProvider
from faker import Faker
from faker.providers import BaseProvider
from model_mommy.recipe import Recipe

from .models import ActionItem


fake = Faker()

actionitem = Recipe(ActionItem)
