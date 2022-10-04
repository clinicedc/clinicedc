from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_offstudy.modelform_mixins import OffstudyNonCrfModelFormMixin
from edc_sites.forms import SiteModelFormMixin

from ..form_validators import ProtocolIncidentFormValidator
from ..models import ProtocolIncident


class ProtocolIncidentForm(
    SiteModelFormMixin,
    OffstudyNonCrfModelFormMixin,
    ActionItemFormMixin,
    BaseModelFormMixin,
    FormValidatorMixin,
    forms.ModelForm,
):
    report_datetime_field_attr = "report_datetime"
    form_validator_cls = ProtocolIncidentFormValidator

    class Meta(ActionItemFormMixin.Meta):
        model = ProtocolIncident
        fields = "__all__"
