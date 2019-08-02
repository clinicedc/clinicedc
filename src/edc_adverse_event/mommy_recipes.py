from faker import Faker
from model_mommy.recipe import Recipe

from .models import CauseOfDeath

fake = Faker()

causeofdeath = Recipe(
    CauseOfDeath, name="cryptococcal_meningitis", short_name="cryptococcal_meningitis"
)
