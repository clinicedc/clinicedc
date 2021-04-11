from django.conf import settings
from edc_notification import GradedEventNotification, ModelNotification, register


@register()
class AeInitialG3EventNotification(GradedEventNotification):

    name = "g3_aeinitial"
    display_name = "Grade 3 initial event reported"
    grade = 3
    model = f"{settings.ADVERSE_EVENT_APP_LABEL}.aeinitial"


@register()
class AeFollowupG3EventNotification(GradedEventNotification):

    name = "g3_aefollowup"
    display_name = "Grade 3 followup event reported"
    grade = 3
    model = f"{settings.ADVERSE_EVENT_APP_LABEL}.aefollowup"


@register()
class AeInitialG4EventNotification(GradedEventNotification):

    name = "g4_aeinitial"
    display_name = "Grade 4 initial event reported"
    grade = 4
    model = f"{settings.ADVERSE_EVENT_APP_LABEL}.aeinitial"


@register()
class AeFollowupG4EventNotification(GradedEventNotification):

    name = "g4_aefollowup"
    display_name = "Grade 4 followup event reported"
    grade = 4
    model = f"{settings.ADVERSE_EVENT_APP_LABEL}.aefollowup"


@register()
class DeathNotification(ModelNotification):

    name = "death"
    display_name = "a death has been reported"
    model = f"{settings.ADVERSE_EVENT_APP_LABEL}.deathreport"
