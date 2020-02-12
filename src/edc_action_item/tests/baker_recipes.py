from faker import Faker
from model_bakery.recipe import Recipe

from ..models import ActionItem


fake = Faker()

actionitem = Recipe(ActionItem)
