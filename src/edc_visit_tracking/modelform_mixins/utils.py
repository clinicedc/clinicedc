from django import forms
from edc_crf.stubs import CrfModelFormStub


def get_subject_visit(modelform: CrfModelFormStub, subject_visit_attr: str):
    if subject_visit_attr not in modelform.cleaned_data:
        subject_visit = getattr(modelform.instance, subject_visit_attr, None)
        if not subject_visit:
            raise forms.ValidationError(f"Field `{subject_visit_attr}` is required (2).")
    else:
        subject_visit = modelform.cleaned_data.get(subject_visit_attr)
    return subject_visit
