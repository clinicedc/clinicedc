from copy import copy
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_constants.constants import YES
from edc_facility.import_holidays import import_holidays
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED

from edc_lab import AliquotCreator, site_labs
from edc_lab.labels.aliquot_label import AliquotLabel, AliquotLabelError
from edc_lab.models import Panel
from edc_lab.tests.site_labs_test_helper import SiteLabsTestHelper
from lab_app.models import SubjectRequisition, SubjectVisit


class TestLabels(TestCase):
    lab_helper = SiteLabsTestHelper()

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel
        self.lab_profile = self.lab_helper.lab_profile
        self.subject_identifier = "1111111111"
        self.helper = Helper(subject_identifier=self.subject_identifier)
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            age_in_years=25,
        )
        self.gender = "M"
        self.initials = "EW"
        self.dob = datetime.now() - relativedelta(years=25)

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
