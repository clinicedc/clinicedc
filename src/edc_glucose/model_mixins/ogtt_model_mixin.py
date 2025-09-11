from django.db import models

from ..model_mixin_factories import ogtt_model_mixin_factory


class OgttModelMixin(ogtt_model_mixin_factory("ogtt"), models.Model):
    """A model mixin of fields for the OGTT"""

    class Meta:
        abstract = True
