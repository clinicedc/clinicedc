from django.test import TestCase
from ..lab import GetModelCls, GetModelError


class TesGetModel(TestCase):

    def test_get_model1(self):
        cls = GetModelCls()
        self.assertRaises(GetModelError, cls.get_model)

    def test_get_model2(self):
        cls = GetModelCls(model='blah')
        self.assertRaises(GetModelError, cls.get_model)

    def test_get_model3(self):
        cls = GetModelCls(model='blah.blah')
        self.assertRaises(GetModelError, cls.get_model)

    def test_get_model4(self):
        cls = GetModelCls(model='auth.user')
        try:
            cls.get_model()
        except GetModelError as e:
            self.fail('GetModelError unexpectedly raised. Got {e}')
