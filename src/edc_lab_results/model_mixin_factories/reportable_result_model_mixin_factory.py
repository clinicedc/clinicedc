from django.db import models

from .field_attrs import get_field_attrs_for_reportable, get_field_attrs_for_utestid

__all__ = ["reportable_result_model_mixin_factory"]


def reportable_result_model_mixin_factory(
    utest_id: str,
    units_choices: tuple,
    default_units: str | None = None,
    verbose_name: str | None = None,
    decimal_places: int | None = None,
    max_digits: int | None = None,
    validators: list | None = None,
    exclude_attrs_for_reportable: bool | None = None,
) -> type[models.Model]:
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
