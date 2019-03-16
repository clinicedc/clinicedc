from django.test import TestCase, tag
from django.test.client import RequestFactory

from ..model_admin_next_url_redirect_mixin import ModelAdminNextUrlRedirectMixin
from ..model_admin_next_url_redirect_mixin import ModelAdminNextUrlRedirectError
from .models import BasicModel, CrfModel, SubjectVisit, RequisitionModel


class TestModelAdmin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_next_url(self):
        obj = BasicModel()
        request = self.factory.get(
            "/?next=my_url_name,arg1,arg2&agr1=value1&arg2=value2&arg3=value3&arg4=value4"
        )
        mixin = ModelAdminNextUrlRedirectMixin()
        self.assertRaises(
            ModelAdminNextUrlRedirectError, mixin.redirect_url, request, obj
        )

    def test_next_url1(self):
        obj = BasicModel()
        request = self.factory.get(
            "/?next=my_url_name,arg1,arg2&arg1=value1&arg2=value2&arg3=value3&arg4=value4"
        )
        mixin = ModelAdminNextUrlRedirectMixin()
        try:
            mixin.redirect_url(request, obj)
        except ModelAdminNextUrlRedirectError as e:
            self.assertIn("my_url_name", str(e))

    def test_next_url4(self):
        obj = BasicModel()
        request = self.factory.get(
            "/?next=my_url_name,arg1,arg2&arg1=value1&arg2=value2&arg3=value3&arg4=value4"
        )
        mixin = ModelAdminNextUrlRedirectMixin()
        try:
            mixin.redirect_url(request, obj)
        except ModelAdminNextUrlRedirectError as e:
            self.assertIn("{'arg1': 'value1', 'arg2': 'value2'}", str(e))

    def test_next_url_with_savenext_crf(self):
        subject_visit = SubjectVisit.objects.create(subject_identifier="12345")
        crf_model = CrfModel.objects.create(subject_visit=subject_visit)
        request = self.factory.post(
            f"/?next=subject_dashboard_url,subject_identifier&"
            f"subject_identifier={crf_model.subject_identifier}",
            {"_savenext": "True"},
        )
        mixin = ModelAdminNextUrlRedirectMixin()
        mixin.show_save_next = True
        mixin.redirect_url(request, crf_model)
        self.assertEqual(
            mixin.redirect_url(request, crf_model),
            f"/subject_dashboard/{subject_visit.subject_identifier}/?"
            f"next=subject_dashboard_url,subject_identifier&"
            f"subject_identifier={subject_visit.subject_identifier}&"
            f"subject_visit={subject_visit.pk}",
        )

    def test_next_url_with_savenext_requisition(self):
        subject_visit = SubjectVisit.objects.create(subject_identifier="12345")
        requisition_model = RequisitionModel.objects.create(subject_visit=subject_visit)
        request = self.factory.post(
            f"/?next=subject_dashboard_url,subject_identifier&"
            f"subject_identifier={requisition_model.subject_identifier}&"
            f"panel_name={requisition_model.panel_name}",
            {"_savenext": "True"},
        )
        mixin = ModelAdminNextUrlRedirectMixin()
        mixin.show_save_next = True
        self.assertEqual(
            mixin.redirect_url(request, requisition_model),
            f"/subject_dashboard/{requisition_model.subject_identifier}/?"
            f"next=subject_dashboard_url,subject_identifier&"
            f"subject_identifier={subject_visit.subject_identifier}&"
            f"subject_visit={subject_visit.pk}",
        )
