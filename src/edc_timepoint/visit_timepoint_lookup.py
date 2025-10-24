from .timepoint_lookup import TimepointLookup


class VisitTimepointLookup(TimepointLookup):
    timepoint_model = "edc_appointment.appointment"
    timepoint_related_model_lookup = "appointment"
