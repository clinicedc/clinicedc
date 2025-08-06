from django import forms
from edc_model_fields.widgets import SliderWidget


class MedicationAdherenceFormMixin:
    visual_score_slider = forms.CharField(
        label="Visual Score", widget=SliderWidget(attrs={"min": 0, "max": 100})
    )
