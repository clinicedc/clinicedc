from django import forms
from django.conf import settings
from edc_utils import convert_php_dateformat


def validate_ae_initial_outcome_date(form_obj):
    ae_initial = form_obj.cleaned_data.get("ae_initial")
    if not ae_initial and form_obj.instance:
        ae_initial = form_obj.instance.ae_initial
    outcome_date = form_obj.cleaned_data.get("outcome_date")
    if ae_initial and outcome_date:
        if outcome_date < ae_initial.ae_start_date:
            formatted_dte = ae_initial.ae_start_date.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
            raise forms.ValidationError(
                {"outcome_date": f"May not be before the AE start date {formatted_dte}."}
            )
