from __future__ import annotations

from edc_consent.modelform_mixins import RequiresConsentModelFormMixin
from edc_form_validators import FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_offstudy.modelform_mixins import OffstudyCrfModelFormMixin
from edc_sites.forms import SiteModelFormMixin
from edc_visit_schedule.modelform_mixins import VisitScheduleCrfModelFormMixin
from edc_visit_tracking.modelform_mixins import VisitTrackingCrfModelFormMixin


class CrfModelFormMixin(
    SiteModelFormMixin,
    RequiresConsentModelFormMixin,
    VisitScheduleCrfModelFormMixin,
    VisitTrackingCrfModelFormMixin,
    OffstudyCrfModelFormMixin,
    BaseModelFormMixin,
    FormValidatorMixin,
):
    """A modelform mixin for all CRFs.

    * Checks for the consent relative to report datetime
      and this schedule;
    * is participant on/off schedule relative to report
      datetime and this schedule;
    * validates subject_visit report datetime;
    * is participant offstudy relative to report datetime.
    """

    report_datetime_field_attr = "report_datetime"
