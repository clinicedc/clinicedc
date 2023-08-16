from edc_notification import GradedEventNotification, ModelNotification, register

from .utils import get_adverse_event_app_label


@register()
class AeInitialG3EventNotification(GradedEventNotification):
    name = "g3_aeinitial"
    display_name = "Grade 3 initial event reported"
    grade = 3
    model = f"{get_adverse_event_app_label()}.aeinitial"


@register()
class AeFollowupG3EventNotification(GradedEventNotification):
    name = "g3_aefollowup"
    display_name = "Grade 3 followup event reported"
    grade = 3
    model = f"{get_adverse_event_app_label()}.aefollowup"


@register()
class AeInitialG4EventNotification(GradedEventNotification):
    name = "g4_aeinitial"
    display_name = "Grade 4 initial event reported"
    grade = 4
    model = f"{get_adverse_event_app_label()}.aeinitial"


@register()
class AeFollowupG4EventNotification(GradedEventNotification):
    name = "g4_aefollowup"
    display_name = "Grade 4 followup event reported"
    grade = 4
    model = f"{get_adverse_event_app_label()}.aefollowup"


@register()
class DeathNotification(ModelNotification):
    name = "death"
    display_name = "a death has been reported"
    model = f"{get_adverse_event_app_label()}.deathreport"
