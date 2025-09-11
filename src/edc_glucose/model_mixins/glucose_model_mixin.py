from __future__ import annotations

from django.db import models

from ..model_mixin_factories import glucose_model_mixin_factory
from .fasting_model_mixin import fasting_model_mixin_factory


class GlucoseModelMixin(
    glucose_model_mixin_factory("glucose"),
    fasting_model_mixin_factory("glucose"),
    models.Model,
):
    """A model mixin of fields for the Glucose, fasting or random"""

    class Meta:
        abstract = True
