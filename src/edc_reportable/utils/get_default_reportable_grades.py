from django.conf import settings

__all__ = ["get_default_reportable_grades"]


def get_default_reportable_grades() -> list[str]:
    return getattr(settings, "EDC_REPORTABLE_DEFAULT_REPORTABLE_GRADES", [3, 4])
