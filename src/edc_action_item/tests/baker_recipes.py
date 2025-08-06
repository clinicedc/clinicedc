from faker import Faker
from model_bakery.recipe import Recipe

from edc_action_item.models import ActionItem

fake = Faker()

actionitem = Recipe(ActionItem)
