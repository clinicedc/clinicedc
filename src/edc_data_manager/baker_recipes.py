from faker import Faker
from model_bakery.recipe import Recipe, related, seq

from .models import QueryRule, DataQuery
from uuid import uuid4

fake = Faker()

queryrule = Recipe(QueryRule, title=str(uuid4()))

dataquery = Recipe(
    DataQuery,
    action_identifier=None,
    parent_action_item=None,
    related_action_item=None,
    title=str(uuid4()),
)
