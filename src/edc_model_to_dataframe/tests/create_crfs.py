import uuid

from clinicedc_tests.models import (
    Crf,
    CrfOne,
    CrfThree,
    CrfTwo,
    ListModel,
    SubjectVisit,
)
from django.utils import timezone

from edc_appointment.models import Appointment

from .create_crfs_with_inlines import create_crf_with_inlines


def create_crfs(i) -> None:
    for ind1, appointment in enumerate(
        Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
    ):
        if ind1 == i:
            break
        SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=timezone.now(),
        )
    for ind2, subject_visit in enumerate(
        SubjectVisit.objects.all().order_by(
            "appointment__subject_identifier",
            "appointment__timepoint",
            "appointment__visit_code_sequence",
        )
    ):
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
            date1=timezone.now(),
            int1=ind2,
            uuid1=uuid.uuid4(),
        )
        CrfOne.objects.create(subject_visit=subject_visit, dte=timezone.now())
        CrfTwo.objects.create(subject_visit=subject_visit, dte=timezone.now())
        CrfThree.objects.create(subject_visit=subject_visit, UPPERCASE=timezone.now())

    for subject_visit in SubjectVisit.objects.all():
        create_crf_with_inlines(subject_visit)
