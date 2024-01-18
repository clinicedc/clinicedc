import uuid

from edc_appointment.models import Appointment
from edc_utils import get_utcnow

from export_app.models import Crf, CrfOne, CrfThree, CrfTwo, ListModel, SubjectVisit

from .create_crfs_with_inlines import create_crf_with_inlines


def create_crfs(i) -> None:
    j = 0
    for appointment in Appointment.objects.all().order_by("timepoint", "visit_code_sequence"):
        j += 1
        if j == i:
            break
        SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=get_utcnow(),
        )
    j = 0
    for subject_visit in SubjectVisit.objects.all().order_by(
        "appointment__subject_identifier",
        "appointment__timepoint",
        "appointment__visit_code_sequence",
    ):
        j += 1
        ListModel.objects.create(
            display_name=(
                f"thing_one_{subject_visit.subject_identifier}"
                f"{subject_visit.appointment.visit_code}"
            ),
            name=(
                f"thing_one_{subject_visit.subject_identifier}"
                f"{subject_visit.appointment.visit_code}"
            ),
        )
        ListModel.objects.create(
            display_name=(
                f"thing_two_{subject_visit.appointment.subject_identifier}"
                f"{subject_visit.appointment.visit_code}"
            ),
            name=(
                f"thing_two_{subject_visit.appointment.subject_identifier}"
                f"{subject_visit.appointment.visit_code}"
            ),
        )
        Crf.objects.create(
            subject_visit=subject_visit,
            char1=f"char{subject_visit.appointment.visit_code}",
            date1=get_utcnow(),
            int1=j,
            uuid1=uuid.uuid4(),
        )
        CrfOne.objects.create(subject_visit=subject_visit, dte=get_utcnow())
        CrfTwo.objects.create(subject_visit=subject_visit, dte=get_utcnow())
        CrfThree.objects.create(subject_visit=subject_visit, UPPERCASE=get_utcnow())

    for subject_visit in SubjectVisit.objects.all():
        create_crf_with_inlines(subject_visit)
