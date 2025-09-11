from django.db import models

from ..model_mixin_factories import fbg_model_mixin_factory


class FbgModelMixin(fbg_model_mixin_factory("fbg"), models.Model):
    """A model mixin of fields for the FBG"""

    class Meta:
        abstract = True
