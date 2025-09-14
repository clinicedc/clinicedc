from django.db import models

from .field_attrs import get_field_attrs_for_utestid

__all__ = ["result_model_mixin_factory"]


def result_model_mixin_factory(
    utest_id: str,
    units_choices: tuple,
    default_units: str | None = None,
    verbose_name: str | None = None,
    decimal_places: int | None = None,
    max_digits: int | None = None,
    validators: list | None = None,
    help_text: str | None = None,
) -> type[models.Model]:
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
