from django.conf import settings


def calculate_avg_bp(
    sys_blood_pressure_one=None,
    sys_blood_pressure_two=None,
    dia_blood_pressure_one=None,
    dia_blood_pressure_two=None,
    **kwargs,
):
    avg_sys = None
    avg_dia = None
    if sys_blood_pressure_one and sys_blood_pressure_two:
        avg_sys = (sys_blood_pressure_one + sys_blood_pressure_two) / 2
    if dia_blood_pressure_one and dia_blood_pressure_two:
        avg_dia = (dia_blood_pressure_one + dia_blood_pressure_two) / 2
    return (avg_sys, avg_dia) if avg_sys and avg_dia else (None, None)


def has_severe_htn(sys=None, dia=None):
    if sys is not None and dia is not None:
        return sys >= get_sys_upper() or dia >= get_dia_upper()
    return None


def get_sys_upper():
    return getattr(settings, "EDC_VITALS_SYS_UPPER", 180)


def get_dia_upper():
    return getattr(settings, "EDC_VITALS_DIA_UPPER", 110)


def has_g3_fever(temperature=None):
    if temperature is not None:
        return get_g3_fever_lower() <= temperature < get_g4_fever_lower()
    return None


def has_g4_fever(temperature=None):
    if temperature is not None:
        return temperature >= get_g4_fever_lower()
    return None


def get_g3_fever_lower():
    return getattr(settings, "EDC_VITALS_G3_FEVER_LOWER", 39.3)


def get_g4_fever_lower():
    return getattr(settings, "EDC_VITALS_G4_FEVER_LOWER", 40.0)
