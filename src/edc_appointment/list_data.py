from django.utils.translation import gettext_lazy as _
from edc_constants.constants import (
    CLINIC,
    ESTIMATED,
    HOME,
    HOSPITAL,
    HOSPITAL_NOTES,
    NOT_APPLICABLE,
    OTHER,
    OUTPATIENT_CARDS,
    PATIENT,
    PATIENT_REPRESENTATIVE,
    TELEPHONE,
)

list_data = {
    "edc_appointment.appointmenttype": [
        (CLINIC, _("In clinic")),
        (HOME, _("At home")),
        (HOSPITAL, _("In hospital")),
        (TELEPHONE, _("By telephone")),
        (NOT_APPLICABLE, _("Not applicable")),
    ],
    "edc_appointment.infosources": [
        (PATIENT, _("Patient")),
        (
            PATIENT_REPRESENTATIVE,
            _("Patient representative (e.g., next of kin, relative, guardian)"),
        ),
        (HOSPITAL_NOTES, _("Hospital notes")),
        (OUTPATIENT_CARDS, _("Outpatient cards")),
        (ESTIMATED, _("Estimated by research staff")),
        (OTHER, _("Other")),
    ],
}
