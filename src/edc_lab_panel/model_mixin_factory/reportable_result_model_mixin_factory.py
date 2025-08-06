from typing import Optional, Type

from django.db import models

from .field_attrs import get_field_attrs_for_reportable, get_field_attrs_for_utestid


def reportable_result_model_mixin_factory(
    utest_id: str,
    units_choices: tuple,
    default_units: Optional[str] = None,
    verbose_name: Optional[str] = None,
    decimal_places: Optional[int] = None,
    max_digits: Optional[int] = None,
    validators: Optional[list] = None,
    exclude_attrs_for_reportable: Optional[bool] = None,
) -> Type[models.Model]:
    """Returns an abstract model class with a single field class"""

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    attrs = get_field_attrs_for_utestid(
        utest_id,
        units_choices,
        default_units,
        verbose_name,
        decimal_places,
        max_digits,
        validators,
    )
    if not exclude_attrs_for_reportable:
        attrs.update(get_field_attrs_for_reportable(utest_id))
    for name, fld_cls in attrs.items():
        AbstractModel.add_to_class(name, fld_cls)
    return AbstractModel
