from django.test import TestCase, tag

from edc_base.model_mixins import BaseUuidModel
from edc_visit_schedule.model_mixins import EnrollmentModelMixin

from ..model_mixins import DisenrollmentModelMixin
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..visit_schedule import VisitScheduleModelError, VisitSchedule
from .models import Enrollment


class ModelC(EnrollmentModelMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'blah'


class ModelD(EnrollmentModelMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'blah.blah'


class ModelE(EnrollmentModelMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_blah.schedule_blah'


class ModelF(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_blah.schedule_blah'


@tag('models')
class TestModels(TestCase):

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False

    def test_str(self):
        site_visit_schedules.loaded = False
        obj = Enrollment(subject_identifier='1111')
        self.assertEqual(str(obj), '1111')

    def test_visit_schedule(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        obj = Enrollment()
        try:
            obj.visit_schedule
        except VisitScheduleModelError:
            pass
        else:
            self.fail('VisitScheduleSiteError unexpectedly not raised.')

    def test_schedule(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        obj = Enrollment()
        try:
            obj.schedule
        except VisitScheduleModelError:
            pass
        else:
            self.fail('VisitScheduleSiteError unexpectedly not raised.')

    def test_visits(self):
        """Asserts can access visits for this  site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        obj = Enrollment()
        try:
            obj.visits
        except VisitScheduleModelError:
            pass
        else:
            self.fail('VisitScheduleSiteError unexpectedly not raised.')

    def test_model_bad_meta(self):
        """Asserts raises if _meta is wrong format.
        """

        site_visit_schedules.loaded = True
        obj = ModelC()
        try:
            obj.visit_schedule
        except VisitScheduleModelError:
            pass
        else:
            self.fail('VisitScheduleModelError unexpectedly not raised')

    def test_model_bad_meta2(self):
        """Asserts raises if _meta is correct format but
        not a valid visit_schedule.schedule pair.
        """
        site_visit_schedules.loaded = True
        obj = ModelD()
        try:
            obj.visit_schedule
        except VisitScheduleModelError:
            pass
        else:
            self.fail('VisitScheduleModelError unexpectedly not raised')

    def test_model_bad_meta3(self):
        """Asserts schedule raises if _meta is wrong format.
        """

        site_visit_schedules.loaded = True
        obj = ModelC()
        try:
            obj.schedule
        except VisitScheduleModelError:
            pass
        else:
            self.fail('VisitScheduleModelError unexpectedly not raised')

    def test_model_bad_meta4(self):
        """Asserts schedule raises if _meta is correct format but
        not a valid visit_schedule.schedule pair.
        """
        site_visit_schedules.loaded = True
        obj = ModelD()
        try:
            obj.schedule
        except VisitScheduleModelError:
            pass
        else:
            self.fail('VisitScheduleModelError unexpectedly not raised')

    def test_natural_key(self):
        v = VisitSchedule(name='visit_schedule_blah')
        s = Schedule(name='schedule_blah', enrollment_model=ModelE,
                     disenrollment_model=ModelF)
        v.add_schedule(s)
        site_visit_schedules.register(v)
        obj = ModelE(subject_identifier='11111')
        obj.save()
        self.assertEqual(obj.natural_key(),
                         ('11111', 'visit_schedule_blah', 'schedule_blah'))
