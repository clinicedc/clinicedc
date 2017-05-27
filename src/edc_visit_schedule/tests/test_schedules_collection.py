from django.test import TestCase, tag

from edc_base.model_mixins import BaseUuidModel

from ..visit_schedule import SchedulesCollection, SchedulesCollectionError


class TestSchedulesCollection(TestCase):

    def test_get_by_model_raises(self):
        """Asserts bad model name raises.
        """
        od = SchedulesCollection()
        self.assertRaises(
            SchedulesCollectionError,
            od._get_schedule_by_model, 'blah')

    def test_get_by_model(self):
        """Asserts can get the object using either model,
        enrollment_model or disenrollment_model
        """

        class TestCollection(SchedulesCollection):
            key = 'key'
            ordering_attr = 'seq'

        class ModelA(BaseUuidModel):
            pass

        class ModelB(BaseUuidModel):
            pass

        class Obj:
            def __init__(self, key, seq):
                self.key = key
                self.seq = seq
                self.enrollment_model = ModelA
                self.disenrollment_model = ModelB

        od = TestCollection()
        obj = Obj('one', 1, )
        od.update({obj.key: obj})
        self.assertEqual(od.get_schedule(model=ModelA), obj)
        self.assertEqual(od.get_schedule(model=ModelB), obj)
