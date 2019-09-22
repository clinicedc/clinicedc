from copy import copy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_constants.constants import YES
from edc_lab import AliquotCreator, site_labs
from edc_lab.labels.aliquot_label import AliquotLabel, AliquotLabelError
from edc_lab.models import Panel
from edc_lab.tests.site_labs_test_helper import SiteLabsTestHelper
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..models import SubjectVisit
from ..models import SubjectRequisition, SubjectConsent
from ..visit_schedules import visit_schedule
from edc_facility.import_holidays import import_holidays


class TestLabels(TestCase):

    lab_helper = SiteLabsTestHelper()

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        self.subject_identifier = "1111111111"
        self.gender = "M"
        self.initials = "EW"
        self.dob = datetime.now() - relativedelta(years=25)
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel

        SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
            identity="1111111",
            confirm_identity="1111111",
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            dob=get_utcnow() - relativedelta(years=25),
        )
        appointment = Appointment.objects.get(visit_code="1000")
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )

        self.subject_requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            requisition_datetime=get_utcnow(),
            drawn_datetime=get_utcnow(),
            is_drawn=YES,
            panel=Panel.objects.get(name=self.panel.name),
        )
        creator = AliquotCreator(
            subject_identifier=self.subject_identifier,
            requisition_identifier=self.subject_requisition.requisition_identifier,
            is_primary=True,
        )
        self.aliquot = creator.create(count=1, aliquot_type=self.panel.aliquot_type)

    def test_aliquot_label(self):
        label = AliquotLabel(pk=self.aliquot.pk)
        self.assertTrue(label.label_context)

    def test_aliquot_label_no_requisition_models_to_query(self):
        requisition_models = copy(site_labs.requisition_models)
        site_labs.requisition_models = []
        label = AliquotLabel(pk=self.aliquot.pk)
        try:
            label.label_context
        except AliquotLabelError:
            pass
        else:
            self.fail("AliquotLabel unexpectedly failed")
        finally:
            site_labs.requisition_models = requisition_models

    def test_aliquot_label_requisition_doesnotexist(self):
        self.aliquot.requisition_identifier = "erik"
        self.aliquot.save()
        label = AliquotLabel(pk=self.aliquot.pk)
        self.assertRaises(AliquotLabelError, getattr, label, "label_context")
