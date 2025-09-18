from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.test.testcases import TestCase
from django.utils import timezone

from edc_action_item.site_action_items import site_action_items
from edc_consent import site_consents
from edc_constants.constants import CLOSED, NO, NOT_APPLICABLE, OPEN, OTHER
from edc_list_data import site_list_data
from edc_protocol_incident import list_data
from edc_protocol_incident.action_items import ProtocolIncidentAction
from edc_protocol_incident.constants import DEVIATION, WITHDRAWN
from edc_protocol_incident.forms import ProtocolIncidentForm
from edc_protocol_incident.models import (
    ActionsRequired,
    ProtocolIncident,
    ProtocolViolations,
)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestProtocolIncident(TestCase):
    def setUp(self):
        site_action_items.registry = {}
        action_cls = ProtocolIncidentAction
        site_action_items.register(action_cls)

        site_list_data.initialize()
        site_list_data.register(list_data, app_name="edc_protocol_incident")
        site_list_data.load_data()

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

        action = ProtocolIncidentAction(subject_identifier=self.subject_identifier)
        self.data = dict(
            action_identifier=action.action_item.action_identifier,
            site=Site.objects.get(id=settings.SITE_ID),
        )

    def test_incident_open_ok(self):
        data = deepcopy(self.data)
        data.update(
            {
                "subject_identifier": self.subject_identifier,
                "report_datetime": timezone.now(),
                "report_status": OPEN,
                "reasons_withdrawn": None,
                "report_type": DEVIATION,
                "safety_impact": NOT_APPLICABLE,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NOT_APPLICABLE,
            }
        )
        obj = ProtocolIncident(**data)
        obj.save()

    def test_incident_open_form(self):
        data = deepcopy(self.data)
        data.update(
            {
                "subject_identifier": "1234",
                "report_datetime": timezone.now(),
                "report_status": OPEN,
                "reasons_withdrawn": None,
                "report_type": DEVIATION,
                "safety_impact": NO,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NO,
                "incident_datetime": timezone.now() - relativedelta(days=3),
                "incident": ProtocolViolations.objects.get(name=OTHER),
                "incident_other": "blah blah",
                "incident_description": "blah blah",
                "incident_reason": "blah blah",
                "violation": None,
            }
        )

        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_incident_try_to_close_form(self):
        data = deepcopy(self.data)
        data.update(
            {
                "subject_identifier": "1234",
                "report_datetime": timezone.now() - relativedelta(days=1),
                "report_status": OPEN,
                "reasons_withdrawn": None,
                "report_type": DEVIATION,
                "safety_impact": NO,
                "short_description": "sdasd asd asdasd ",
                "study_outcomes_impact": NO,
                "incident_datetime": timezone.now() - relativedelta(days=3),
                "incident": ProtocolViolations.objects.get(name=OTHER),
                "incident_other": "blah blah",
                "incident_description": "blah blah",
                "incident_reason": "blah blah",
                "violation": None,
            }
        )

        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        # self.assertIn("corrective_action_datetime", form._errors)
        data.update(corrective_action_datetime=timezone.now())
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("corrective_action", form._errors)

        data.update(corrective_action="we took corrective action")
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        # self.assertIn("preventative_action_datetime", form._errors)

        data.update(preventative_action_datetime=timezone.now())
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("preventative_action", form._errors)

        data.update(preventative_action="we took preventative action", report_status=CLOSED)
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("action_required", form._errors)

        data.update(action_required=ActionsRequired.objects.get(name="remain_on_study"))
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("report_closed_datetime", form._errors)

        data.update(report_closed_datetime=timezone.now())
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertEqual({}, form._errors)

        data.update(report_status=WITHDRAWN)
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertIn("reasons_withdrawn", form._errors)

        data.update(reasons_withdrawn="cause i feel like it")
        form = ProtocolIncidentForm(data=data, instance=ProtocolIncident())
        form.is_valid()
        self.assertEqual({}, form._errors)
