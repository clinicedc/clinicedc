from __future__ import annotations

from edc_utils.round_up import round_half_away_from_zero

from ..data import molecular_weights
from ..exceptions import ConversionNotHandled
from ..units import (
    GRAMS_PER_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
)

__all__ = ["convert_units"]


class UnitsConverter:
    def __init__(
        self,
        label: str = None,
        value: int | float | None = None,
        units_from: str | None = None,
        units_to: str | None = None,
        places: int | None = None,
    ):
        self.label = label
        self.value = value
        self.units_from = units_from
        self.units_to = units_to
        self.places = places or 4

        if label is None:
            raise ValueError("label is required. See convert_units.")
        elif value is not None and units_from and units_to and units_from != units_to:
            self.converted_value = self.get_converted_value()
        elif units_from == units_to:
            self.converted_value = value
        else:
            raise ConversionNotHandled(
                f"Conversion not handled. Tried {label} from {units_from} to {units_to}."
            )

    def get_mw(self):
        mw = molecular_weights.get(self.label)
        if not mw:
            raise ConversionNotHandled(
                f"Conversion not handled. Molecular weight not found for {self.label}."
            )
        return mw

    def round_up(self, converted_value):
        try:
            converted_value = round_half_away_from_zero(converted_value, self.places)
        except TypeError as e:
            raise ConversionNotHandled(
                f"Conversion not handled. Tried {self.label} from {self.units_from} "
                f"to {self.units_to}. "
                f"Got {e} when rounding {converted_value} to {self.places} places."
            )
        return converted_value

    def from_milligrams_per_deciliter(self):
        converted_value = None
        if self.units_to == MILLIMOLES_PER_LITER:
            converted_value = (self.value * 10.00) / self.get_mw()
        elif self.units_to == MICROMOLES_PER_LITER:
            converted_value = (self.value * 10.00**3) / self.get_mw()
        elif self.units_to == GRAMS_PER_LITER:
            converted_value = float(self.value) / 100.00
        return converted_value

    def from_grams_per_liter(self):
        converted_value = None
        if self.units_to == MILLIMOLES_PER_LITER:
            converted_value = (self.value * 1000.00) / self.get_mw()
        elif self.units_to == MICROMOLES_PER_LITER:
            converted_value = (self.value * 10.00**6) / self.get_mw()
        elif self.units_to == MILLIGRAMS_PER_DECILITER:
            converted_value = float(self.value) * 100.00
        return converted_value

    def from_millimoles_per_liter(self):
        converted_value = None
        if self.units_to == MICROMOLES_PER_LITER:
            converted_value = self.value * 1000.00
        elif self.units_to == GRAMS_PER_LITER:
            converted_value = (self.value * self.get_mw()) / 1000.00
        elif self.units_to == MILLIGRAMS_PER_DECILITER:
            converted_value = (self.value * self.get_mw()) / 10.00
        return converted_value

    def from_micromoles_per_liter(self):
        converted_value = None
        if self.units_to == MILLIMOLES_PER_LITER:
            converted_value = self.value / 1000.00
        elif self.units_to == GRAMS_PER_LITER:
            converted_value = (self.value * self.get_mw()) / 10**6
        elif self.units_to == MILLIGRAMS_PER_DECILITER:
            converted_value = (self.value * self.get_mw()) / 10**3
        return converted_value

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
    label: str = None,
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
