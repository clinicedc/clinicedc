from __future__ import annotations

from django.db import models

from ..model_mixin_factories import fasting_model_mixin_factory


class FastingModelMixin(fasting_model_mixin_factory(), models.Model):
    """A model mixin of fields about fasting.

    Used together with mixins for glucose measurements.
    """

    class Meta:
        abstract = True
