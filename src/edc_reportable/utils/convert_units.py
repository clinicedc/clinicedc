from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist

from edc_utils.round_up import round_half_away_from_zero

from ..exceptions import ConversionNotHandled
from ..units import (
    GRAMS_PER_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIGRAMS_PER_LITER,
    MILLIMOLES_PER_LITER,
)
from .molecular_weight_model_cls import molecular_weight_model_cls

__all__ = ["convert_units"]


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


def micromoles_per_liter_to(*, label: str, value: float | int, units_to: str) -> dict:
    if units_to == MICROMOLES_PER_LITER:
        return {MICROMOLES_PER_LITER: float(value)}
    if units_to == MILLIMOLES_PER_LITER:
        return {MILLIMOLES_PER_LITER: float(value) / 1000.00}
    if units_to == GRAMS_PER_LITER:
        return {GRAMS_PER_LITER: (float(value) * get_mw(label)) / 100.00}
    if units_to == MILLIGRAMS_PER_DECILITER:
        return {MILLIGRAMS_PER_DECILITER: (float(value) * get_mw(label)) / 10000.00}
    raise ConversionNotHandled(f"Conversion not found. Tried umol/L to {units_to}. ")


def milligrams_per_deciliter_to(
    *, label: str, value: float | int, units_to: str
) -> dict[str, float]:
    if units_to == MILLIGRAMS_PER_DECILITER:
        return {MILLIGRAMS_PER_DECILITER: float(value)}
    if units_to == MILLIMOLES_PER_LITER:
        return {MILLIMOLES_PER_LITER: (float(value) * 10.00) / get_mw(label)}
    if units_to == MICROMOLES_PER_LITER:
        return {MICROMOLES_PER_LITER: (float(value) * 10000.00) / get_mw(label)}
    if units_to == MILLIGRAMS_PER_LITER:
        return {MILLIGRAMS_PER_LITER: float(value) * 10.00}
    if units_to == GRAMS_PER_LITER:
        return {GRAMS_PER_LITER: float(value) / 100.00}
    raise ConversionNotHandled(f"Conversion not found. Tried mg/dL to {units_to}. ")


class UnitsConverter:
    def __init__(
        self,
        *,
        label: str,
        value: int | float,
        units_from: str,
        units_to: str,
        places: int | None = None,
    ):
        self.label = label
        self.value = value
        self.units_from = units_from
        self.units_to = units_to
        self.places = places or 4

        if label is None:
            raise ValueError("label is required. See convert_units.")
        if value is not None and units_from and units_to and units_from != units_to:
            self.converted_value = self.get_converted_value()
        elif units_from == units_to:
            self.converted_value = value
        else:
            raise ConversionNotHandled(
                f"Conversion not handled. Tried {label} from {units_from} to {units_to}."
            )

    def get_mw(self):
        return get_mw(self.label)

    def round_up(self, converted_value):
        try:
            converted_value = round_half_away_from_zero(converted_value, self.places)
        except TypeError as e:
            raise ConversionNotHandled(
                f"Conversion not handled. Tried {self.label} from {self.units_from} "
                f"to {self.units_to}. "
                f"Got {e} when rounding {converted_value} to {self.places} places."
            ) from e
        return converted_value

    def from_milligrams_per_deciliter(self) -> float | int:
        if self.units_to != MILLIGRAMS_PER_DECILITER:
            return milligrams_per_deciliter_to(
                label=self.label, value=float(self.value), units_to=self.units_to
            )[self.units_to]
        return self.value

    def from_grams_per_liter(self) -> float | int:
        if self.units_to != GRAMS_PER_LITER:
            return milligrams_per_deciliter_to(
                label=self.label,
                value=float(self.value) * 100.00,
                units_to=self.units_to,
            )[self.units_to]
        return self.value

    def from_millimoles_per_liter(self) -> float | int:
        if self.units_to != MILLIMOLES_PER_LITER:
            return micromoles_per_liter_to(
                label=self.label, value=self.value / 1000, units_to=self.units_to
            )[self.units_to]
        return self.value

    def from_micromoles_per_liter(self):
        if self.units_to != MICROMOLES_PER_LITER:
            return micromoles_per_liter_to(
                label=self.label, value=self.value, units_to=self.units_to
            )[self.units_to]
        return self.value

    def get_converted_value(self) -> int | float:
        converted_value = None
        if self.units_from == MILLIGRAMS_PER_DECILITER:
            converted_value = self.from_milligrams_per_deciliter()
        elif self.units_from == GRAMS_PER_LITER:
            converted_value = self.from_grams_per_liter()
        elif self.units_from == MILLIMOLES_PER_LITER:
            converted_value = self.from_millimoles_per_liter()
        elif self.units_from == MICROMOLES_PER_LITER:
            converted_value = self.from_micromoles_per_liter()
        if not converted_value:
            raise ConversionNotHandled(
                f"Conversion not handled. Tried {self.label} from "
                f"{self.units_from} to {self.units_to}."
            )
        return self.round_up(converted_value)


def convert_units(
    *,
    label: str | None = None,
    value: int | float | None = None,
    units_from: str | None = None,
    units_to: str | None = None,
    places: int | None = None,
):
    return UnitsConverter(
        label=label,
        value=value,
        units_from=units_from,
        units_to=units_to,
        places=places,
    ).converted_value
