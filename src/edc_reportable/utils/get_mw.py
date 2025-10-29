from __future__ import annotations

from clinicedc_utils import ConversionNotHandled
from django.core.exceptions import ObjectDoesNotExist

from .molecular_weight_model_cls import molecular_weight_model_cls

__all__ = ["get_mw"]


def get_mw(label):
    try:
        molecular_weight = molecular_weight_model_cls().objects.get(label=label)
    except ObjectDoesNotExist as e:
        raise ConversionNotHandled(
            f"Conversion not handled. Molecular weight not found for {label}."
        ) from e
    else:
        mw = molecular_weight.mw
    return mw
