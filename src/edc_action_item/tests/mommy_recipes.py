from faker import Faker
from model_mommy.recipe import Recipe

from ..models import ActionItem


fake = Faker()

actionitem = Recipe(ActionItem)
