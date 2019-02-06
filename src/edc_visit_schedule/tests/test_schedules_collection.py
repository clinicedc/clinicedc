from django.test import TestCase, tag

from ..visit_schedule import SchedulesCollection, SchedulesCollectionError


class TestSchedulesCollection(TestCase):
    def setUp(self):
        class TestCollection(SchedulesCollection):
            key = "key"
            ordering_attr = "seq"

        class Obj:
            def __init__(self, key, seq):
                self.key = key
                self.seq = seq
                self.onschedule_model = "app_label.onschedule"
                self.offschedule_model = "app_label.offschedule"

            def validate(self, visit_schedule_name=None):
                return None

        self.test_collection = TestCollection()
        self.dummy_schedule = Obj("one", 1)
        self.test_collection.update({self.dummy_schedule.key: self.dummy_schedule})

    def test_get_by_model_raises(self):
        """Asserts bad model name raises.
        """
        obj = SchedulesCollection()
        self.assertRaises(SchedulesCollectionError, obj.get_schedule, "blah")

    def test_get_by_model(self):
        """Asserts can get the object using either model,
        onschedule_model or offschedule_model
        """
        self.assertEqual(
            self.test_collection.get_schedule(model="app_label.onschedule"),
            self.dummy_schedule,
        )
        self.assertEqual(
            self.test_collection.get_schedule("app_label.onschedule"),
            self.dummy_schedule,
        )

    def test_validate(self):
        self.test_collection.validate()
