from .units import MICROMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER, MILLIMOLES_PER_LITER


class ConversionNotHandled(Exception):
    pass


def convert_units(value, units_from=None, units_to=None, places=None):
    places = places or 4
    converted_value = value
    if value and units_from and units_to and units_from != units_to:
        if (units_from, units_to) == (MILLIGRAMS_PER_DECILITER, MILLIMOLES_PER_LITER):
            converted_value = float(value) / 18.018018
        elif (units_from, units_to) == (MILLIMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER):
            converted_value = float(value) * 18.018018
        elif (units_from, units_to) == (MILLIGRAMS_PER_DECILITER, MICROMOLES_PER_LITER):
            converted_value = float(value) * 88.42
        elif (units_from, units_to) == (MICROMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER):
            converted_value = float(value) / 88.42
        else:
            raise ConversionNotHandled(
                f"Conversion not handled. Got from {units_from} to {units_to}"
            )
    if converted_value:
        converted_value = round(converted_value, places)
    return converted_value
