from django.test import TestCase, tag
from django.test.client import RequestFactory

from ...model_admin_next_url_redirect_mixin import ModelAdminNextUrlRedirectError
from ...model_admin_next_url_redirect_mixin import ModelAdminNextUrlRedirectMixin
from ..models import BasicModel
from ..reference_configs import register_to_site_reference_configs


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
