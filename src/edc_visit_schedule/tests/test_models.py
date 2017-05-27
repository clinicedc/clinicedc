from django.test import TestCase, tag

from edc_base.model_mixins import BaseUuidModel
from edc_visit_schedule.model_mixins import EnrollmentModelMixin

from ..site_visit_schedules import site_visit_schedules
from ..visit_schedule import VisitScheduleModelError
from .models import Enrollment


class ModelC(EnrollmentModelMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'blah'


class ModelD(EnrollmentModelMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'blah.blah'


@tag('models')
class TestModels(TestCase):

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
