from typing import Optional, Type

from django.db import models

from .field_attrs import get_field_attrs_for_utestid


def result_model_mixin_factory(
    utest_id: str,
    units_choices: tuple,
    default_units: Optional[str] = None,
    verbose_name: Optional[str] = None,
    decimal_places: Optional[int] = None,
    max_digits: Optional[int] = None,
    validators: Optional[list] = None,
    help_text: Optional[str] = None,
) -> Type[models.Model]:
    """Returns an abstract model class with a single field class"""

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    for name, fld_cls in get_field_attrs_for_utestid(
        utest_id,
        units_choices,
        default_units,
        verbose_name,
        decimal_places,
        max_digits,
        validators,
        help_text,
    ):
        AbstractModel.add_to_class(name, fld_cls)
    return AbstractModel
