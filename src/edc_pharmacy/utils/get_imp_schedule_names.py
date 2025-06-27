from django.conf import settings


def get_imp_schedule_names() -> tuple[list[str], list[str]]:
    imp_schedule_names = getattr(
        settings, "EDC_PHARMACY_IMP_VISIT_SCHEDULES", ["visit_schedule.schedule"]
    )
    visit_schedule_names = []
    schedule_names = []
    for imp_schedule_name in imp_schedule_names:
        v, s = imp_schedule_name.split(".")
        visit_schedule_names.append(v)
        schedule_names.append(s)
    return visit_schedule_names, schedule_names
