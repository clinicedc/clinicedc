from faker import Faker
from model_bakery.recipe import Recipe

from .models import CauseOfDeath

fake = Faker()

causeofdeath = Recipe(
    CauseOfDeath, display_name="cryptococcal_meningitis", name="cryptococcal_meningitis"
)
