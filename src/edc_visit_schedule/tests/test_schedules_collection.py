from django.test import TestCase, tag

from ..visit_schedule import SchedulesCollection, SchedulesCollectionError


class TestSchedulesCollection(TestCase):

    def setUp(self):

        class TestCollection(SchedulesCollection):
            key = 'key'
            ordering_attr = 'seq'

        class Obj:
            def __init__(self, key, seq):
                self.key = key
                self.seq = seq
                self.enrollment_model = 'app_label.enrollment'
                self.disenrollment_model = 'app_label.disenrollment'

            def validate(self, visit_schedule_name=None):
                return None

        self.test_collection = TestCollection()
        self.dummy_schedule = Obj('one', 1, )
        self.test_collection.update(
            {self.dummy_schedule.key: self.dummy_schedule})

    def test_get_by_model_raises(self):
        """Asserts bad model name raises.
        """
        obj = SchedulesCollection()
        self.assertRaises(SchedulesCollectionError, obj.get_schedule, 'blah')

    def test_get_by_model(self):
        """Asserts can get the object using either model,
        enrollment_model or disenrollment_model
        """
        self.assertEqual(
            self.test_collection.get_schedule(model='app_label.enrollment'),
            self.dummy_schedule)
        self.assertEqual(
            self.test_collection.get_schedule('app_label.enrollment'),
            self.dummy_schedule)

    def test_validate(self):
        self.test_collection.validate()
