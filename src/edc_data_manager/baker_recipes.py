from uuid import uuid4

from faker import Faker
from model_bakery.recipe import Recipe

from .models import DataQuery, QueryRule

fake = Faker()

queryrule = Recipe(QueryRule, title=str(uuid4()))

dataquery = Recipe(
    DataQuery,
    action_identifier=None,
    parent_action_item=None,
    related_action_item=None,
    title=str(uuid4()),
)
