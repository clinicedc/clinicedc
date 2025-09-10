from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.conf import settings
from django.contrib.sites.models import Site
from django.test.testcases import TestCase

from edc_action_item.site_action_items import site_action_items
from edc_consent import site_consents
from edc_constants.constants import CLOSED, NOT_APPLICABLE, OPEN, OTHER, YES
from edc_list_data import site_list_data
from edc_protocol_incident import list_data
from edc_protocol_incident.action_items import ProtocolDeviationViolationAction
from edc_protocol_incident.constants import DEVIATION, VIOLATION
from edc_protocol_incident.forms import ProtocolDeviationViolationForm
from edc_protocol_incident.models import (
    ActionsRequired,
    ProtocolDeviationViolation,
    ProtocolViolations,
)
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestProtocolViolation(TestCase):
    def setUp(self):
        site_action_items.registry = {}
        action_cls = ProtocolDeviationViolationAction
        site_action_items.register(action_cls)
        site_list_data.initialize()
        site_list_data.register(list_data, app_name="edc_protocol_incident")

        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )
        self.subject_identifier = consent.subject_identifier

        action = ProtocolDeviationViolationAction(
            subject_identifier=self.subject_identifier
        )
        self.data = dict(
            action_identifier=action.action_item.action_identifier,
            site=Site.objects.get(id=settings.SITE_ID),
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

        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
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

        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("corrective_action_datetime", form._errors)
        data.update(corrective_action_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("corrective_action", form._errors)

        data.update(corrective_action="we took corrective action")
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("preventative_action_datetime", form._errors)

        data.update(preventative_action_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("preventative_action", form._errors)

        data.update(preventative_action="we took preventative action")
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("action_required", form._errors)

        data.update(action_required=ActionsRequired.objects.get(name="remain_on_study"))
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("report_closed_datetime", form._errors)

        data.update(report_closed_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
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

        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("safety_impact", form._errors)

        data.update({"safety_impact": YES})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("safety_impact_details", form._errors)

        data.update({"safety_impact_details": "blah blah"})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("study_outcomes_impact", form._errors)

        data.update({"study_outcomes_impact": YES})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("study_outcomes_impact_details", form._errors)

        data.update({"study_outcomes_impact_details": "details details ..."})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("violation_datetime", form._errors)

        data.update({"violation_datetime": get_utcnow()})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("violation", form._errors)

        data.update({"violation": ProtocolViolations.objects.get(name=OTHER)})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("violation_other", form._errors)

        data.update({"violation_other": "a bad violation"})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("violation_description", form._errors)

        data.update({"violation_description": "a violation is better described"})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("violation_reason", form._errors)

        data.update({"violation_reason": "a violation is better reasoned"})
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("corrective_action_datetime", form._errors)

        data.update(corrective_action_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("corrective_action", form._errors)

        data.update(corrective_action="we took corrective action")
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("preventative_action_datetime", form._errors)

        data.update(preventative_action_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("preventative_action", form._errors)

        data.update(preventative_action="we took preventative action")
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("action_required", form._errors)

        data.update(action_required=ActionsRequired.objects.get(name="remain_on_study"))
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertIn("report_closed_datetime", form._errors)

        data.update(report_closed_datetime=get_utcnow())
        form = ProtocolDeviationViolationForm(
            data=data, instance=ProtocolDeviationViolation()
        )
        form.is_valid()
        self.assertEqual({}, form._errors)
