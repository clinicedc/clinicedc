from edc_action_item.modelform_mixins import ActionItemModelFormMixin
from edc_form_validators import FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_offstudy.modelform_mixins import OffstudyNonCrfModelFormMixin
from edc_sites.forms import SiteModelFormMixin


class AeModelFormMixin(
    SiteModelFormMixin,
    OffstudyNonCrfModelFormMixin,
    ActionItemModelFormMixin,
    FormValidatorMixin,
    BaseModelFormMixin,
):
    pass
