from django.db import models

from ..screening_identifier import ScreeningIdentifier
from .screening_fields_model_mixin import ScreeningFieldsModeMixin
from .screening_identifier_model_mixin import ScreeningIdentifierModelMixin
from .screening_methods_model_mixin import ScreeningMethodsModeMixin


class ScreeningModelMixin(
    ScreeningMethodsModeMixin,
    ScreeningIdentifierModelMixin,
    ScreeningFieldsModeMixin,
    models.Model,
):

    """You may wish to also include the `EligibilityModelMixin`
    in your declaration."""

    identifier_cls = ScreeningIdentifier

    class Meta:
        abstract = True
