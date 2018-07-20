from copy import copy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import YES
from edc_registration.models import RegisteredSubject

from ..lab.aliquot_creator import AliquotCreator
from ..labels.aliquot_label import AliquotLabel, AliquotLabelError
from ..models.panel import Panel
from ..site_labs import site_labs
from .models import SimpleSubjectVisit as SubjectVisit
from .models import SubjectRequisition
from .site_labs_test_helper import SiteLabsTestHelper


class TestLabels(TestCase):

    lab_helper = SiteLabsTestHelper()

    def setUp(self):
        self.subject_identifier = '1111111111'
        self.gender = 'M'
        self.initials = 'EW'
        self.dob = datetime.now() - relativedelta(years=25)
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier,
            initials=self.initials,
            dob=self.dob,
            gender=self.gender)
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier)
        self.subject_requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            requisition_datetime=get_utcnow(),
            drawn_datetime=get_utcnow(),
            is_drawn=YES,
            panel=Panel.objects.get(name=self.panel.name))
        creator = AliquotCreator(
            subject_identifier=self.subject_identifier,
            requisition_identifier=self.subject_requisition.requisition_identifier,
            is_primary=True)
        self.aliquot = creator.create(
            count=1, aliquot_type=self.panel.aliquot_type)

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
            self.fail('AliquotLabel unexpectedly failed')
        finally:
            site_labs.requisition_models = requisition_models

    def test_aliquot_label_requisition_doesnotexist(self):
        self.aliquot.requisition_identifier = 'erik'
        self.aliquot.save()
        label = AliquotLabel(pk=self.aliquot.pk)
        self.assertRaises(AliquotLabelError, getattr, label, 'label_context')
