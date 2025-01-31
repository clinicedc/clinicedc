from edc_utils import get_utcnow

from model_to_dataframe_app.models import CrfWithInline, ListOne, ListTwo


def create_crf_with_inlines(subject_visit):
    list_one = ListOne.objects.create(
        display_name=f"list_one{subject_visit.subject_identifier}{subject_visit.visit_code}",
        name=f"list_one{subject_visit.subject_identifier}{subject_visit.visit_code}",
    )
    list_two = ListTwo.objects.create(
        display_name=f"list_two{subject_visit.subject_identifier}{subject_visit.visit_code}",
        name=f"list_two{subject_visit.subject_identifier}{subject_visit.visit_code}",
    )
    CrfWithInline.objects.create(
        subject_visit=subject_visit,
        list_one=list_one,
        list_two=list_two,
        dte=get_utcnow(),
    )
