from copy import deepcopy

from django.test.testcases import TestCase
from edc_action_item import site_action_items
from edc_constants.constants import CLOSED, NOT_APPLICABLE, OPEN, OTHER, YES
from edc_list_data import site_list_data
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_protocol_incident import list_data
from edc_protocol_incident.constants import DEVIATION, VIOLATION
from edc_protocol_incident.forms import ProtocolDeviationViolationForm
from edc_protocol_incident.models import (
    ActionsRequired,
    ProtocolDeviationViolation,
    ProtocolViolations,
)

from ..action_items import ProtocolDeviationViolationAction
from ..visit_schedule import visit_schedule


class TestProtocolViolation(TestCase):
    def setUp(self):
        site_action_items.registry = {}
        action_cls = ProtocolDeviationViolationAction
        site_action_items.register(action_cls)
        site_list_data.initialize()
        site_list_data.register(list_data, app_name="edc_protocol_incident")
        site_list_data.load_data()
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        self.subject_identifier = "1234"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

        action = ProtocolDeviationViolationAction(subject_identifier=self.subject_identifier)
        self.data = dict(
            action_identifier=action.action_item.action_identifier,
        )

    def test_deviation_open_ok(self):
        data = deepcopy(self.data)
        data.update(
            {
                "subject_identifier": self.subject_identifier,
                "report_datetime": get_utcnow(),
                "report_status": OPEN,
                "report_type": DEVIATION,
                "safety_impact": NOT_APPLICABLE,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NOT_APPLICABLE,
            }
        )
        obj = ProtocolDeviationViolation(**data)
        obj.save()

    def test_deviation_open_form(self):
        data = deepcopy(self.data)
        data.update(
            {
                "subject_identifier": "1234",
                "report_datetime": get_utcnow(),
                "report_status": OPEN,
                "report_type": DEVIATION,
                "safety_impact": NOT_APPLICABLE,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NOT_APPLICABLE,
                "violation": None,
            }
        )

        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_deviation_try_to_close_form(self):
        data = deepcopy(self.data)
        data.update(
            {
                "subject_identifier": "1234",
                "report_datetime": get_utcnow(),
                "report_status": CLOSED,
                "report_type": DEVIATION,
                "safety_impact": NOT_APPLICABLE,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NOT_APPLICABLE,
                "violation": None,
            }
        )

        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("corrective_action_datetime", form._errors)
        data.update(corrective_action_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("corrective_action", form._errors)

        data.update(corrective_action="we took corrective action")
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("preventative_action_datetime", form._errors)

        data.update(preventative_action_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("preventative_action", form._errors)

        data.update(preventative_action="we took preventative action")
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("action_required", form._errors)

        data.update(action_required=ActionsRequired.objects.get(name="remain_on_study"))
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("report_closed_datetime", form._errors)

        data.update(report_closed_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_violation_try_to_close_form(self):
        data = deepcopy(self.data)
        data.update(
            {
                "subject_identifier": "1234",
                "report_datetime": get_utcnow(),
                "report_status": CLOSED,
                "report_type": VIOLATION,
                "short_description": "sdasd asd asdasd ",
                "safety_impact": NOT_APPLICABLE,
                "study_outcomes_impact": NOT_APPLICABLE,
            }
        )

        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("safety_impact", form._errors)

        data.update({"safety_impact": YES})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("safety_impact_details", form._errors)

        data.update({"safety_impact_details": "blah blah"})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("study_outcomes_impact", form._errors)

        data.update({"study_outcomes_impact": YES})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("study_outcomes_impact_details", form._errors)

        data.update({"study_outcomes_impact_details": "details details ..."})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("violation_datetime", form._errors)

        data.update({"violation_datetime": get_utcnow()})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("violation", form._errors)

        data.update({"violation": ProtocolViolations.objects.get(name=OTHER)})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("violation_other", form._errors)

        data.update({"violation_other": "a bad violation"})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("violation_description", form._errors)

        data.update({"violation_description": "a violation is better described"})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("violation_reason", form._errors)

        data.update({"violation_reason": "a violation is better reasoned"})
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("corrective_action_datetime", form._errors)

        data.update(corrective_action_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("corrective_action", form._errors)

        data.update(corrective_action="we took corrective action")
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("preventative_action_datetime", form._errors)

        data.update(preventative_action_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("preventative_action", form._errors)

        data.update(preventative_action="we took preventative action")
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("action_required", form._errors)

        data.update(action_required=ActionsRequired.objects.get(name="remain_on_study"))
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertIn("report_closed_datetime", form._errors)

        data.update(report_closed_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(data=data, instance=ProtocolDeviationViolation())
        form.is_valid()
        self.assertEqual({}, form._errors)
