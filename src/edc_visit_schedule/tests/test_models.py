from django.test import TestCase, tag
from edc_base.model_mixins import BaseUuidModel
from edc_visit_schedule.model_mixins import OnScheduleModelMixin
from uuid import uuid4

from ..model_mixins import OffScheduleModelMixin, VisitScheduleMethodsError
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..visit_schedule import VisitSchedule
from .models import OnSchedule


class ModelC(OnScheduleModelMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'blah'


class ModelD(OnScheduleModelMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'blah.blah'


class ModelE(OnScheduleModelMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        consent_model = 'edc_visit_schedule.subjectconsent'
        visit_schedule_name = 'visit_schedule_blah.schedule_blah'


class ModelF(OffScheduleModelMixin, BaseUuidModel):

    class Meta(OffScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_blah.schedule_blah'


class ModelG(OnScheduleModelMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule1.schedule1'


class ModelG2(OffScheduleModelMixin, BaseUuidModel):

    class Meta(OffScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule1.schedule1'


@tag('models')
class TestModels(TestCase):

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False

    def test_str(self):
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        obj = OnSchedule(subject_identifier='1111')
        self.assertEqual(str(obj), '1111')

    def test_visit_schedule(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        obj = OnSchedule()
        try:
            obj.visit_schedule
        except VisitScheduleMethodsError:
            pass
        else:
            self.fail('VisitScheduleSiteError unexpectedly not raised.')

    def test_schedule(self):
        """Asserts cannot access without site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        obj = OnSchedule()
        try:
            obj.schedule
        except VisitScheduleMethodsError:
            pass
        else:
            self.fail('VisitScheduleSiteError unexpectedly not raised.')

    def test_visits(self):
        """Asserts can access visits for this  site_visit_schedule loaded.
        """
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        obj = OnSchedule()
        try:
            obj.visits
        except VisitScheduleMethodsError:
            pass
        else:
            self.fail('VisitScheduleSiteError unexpectedly not raised.')

    def test_model_meta(self):
        """Asserts accepts apha-numeric pattern.
        """
        visit_schedule = VisitSchedule(
            name='visit_schedule1',
            verbose_name='Visit Schedule',
            app_label='edc_visit_schedule',
            visit_model='edc_visit_schedule.SubjectVisit',
            offstudy_model='edc_visit_schedule.SubjectOffstudy',
            death_report_model='edc_visit_schedule.DeathReport')

        schedule = Schedule(
            name='schedule1',
            onschedule_model='edc_visit_schedule.ModelG',
            offschedule_model='edc_visit_schedule.ModelG2')
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        obj = ModelG()
        obj.visit_schedule

    def test_model_bad_meta(self):
        """Asserts raises if _meta is wrong format.
        """

        site_visit_schedules.loaded = True
        obj = ModelC()
        try:
            obj.visit_schedule
        except VisitScheduleMethodsError:
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
        except VisitScheduleMethodsError:
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
        except VisitScheduleMethodsError:
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
        except VisitScheduleMethodsError:
            pass
        else:
            self.fail('VisitScheduleModelError unexpectedly not raised')

    def test_natural_key(self):
        v = VisitSchedule(name='visit_schedule_blah')
        s = Schedule(name='schedule_blah', onschedule_model='edc_visit_schedule.ModelE',
                     offschedule_model='edc_visit_schedule.ModelF')
        v.add_schedule(s)
        site_visit_schedules.register(v)
        obj = ModelE(
            subject_identifier='11111',
            consent_identifier=uuid4())
        obj.save()
        self.assertEqual(obj.natural_key(),
                         ('11111', 'visit_schedule_blah', 'schedule_blah'))
