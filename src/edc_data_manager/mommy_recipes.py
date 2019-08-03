from faker import Faker
from model_mommy.recipe import Recipe, related, seq

from .models import QueryRule, DataQuery
from uuid import uuid4

fake = Faker()


queryrule = Recipe(QueryRule, title=str(uuid4()))

dataquery = Recipe(DataQuery, action_identifier=None, title=str(uuid4()))
