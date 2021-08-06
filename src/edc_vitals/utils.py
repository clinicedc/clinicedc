def calculate_avg_bp(
    sys_blood_pressure_one=None,
    sys_blood_pressure_two=None,
    dia_blood_pressure_one=None,
    dia_blood_pressure_two=None,
    **kwargs
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
        return sys >= 180 or dia >= 120
    return None
