from django.test import TestCase

from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.membership_form import MembershipForm
from edc_visit_schedule.visit import Visit, Crf
from edc_visit_schedule.visit_schedule import VisitSchedule
from edc_visit_schedule.exceptions import VisitScheduleError, AlreadyRegistered, ScheduleError, VisitError, CrfError

from example.models import SubjectConsent, SubjectVisit


bad_visit_schedule = VisitSchedule(
    name='Bad Visit Schedule',
    app_label='example',
)


class TestVisitSchedule(TestCase):

    def setUp(self):
        self.bad_visit_schedule = VisitSchedule(
            name='Bad Visit Schedule',
            app_label='example',
        )

    @property
    def visit_schedule(self):
        return site_visit_schedules.get_visit_schedule('example')

    def test_get_schedules(self):
        pass

    def test_get_visit_definitions_for_membership_form(self):
        pass

    def test_visit_schedule_gets_membership_form(self):
        self.assertIsInstance(
            self.visit_schedule.get_membership_form('example', 'subjectconsent'),
            MembershipForm)

    def test_schedule_get_visits_by_model(self):
        for schedule in self.visit_schedule.schedules.values():
            self.assertIsInstance(
                schedule.get_visits_by_visit_model(SubjectVisit), list)

    def test_schedule_get_visits_by_model2(self):
        for schedule in self.visit_schedule.schedules.values():
            for visit in schedule.get_visits_by_visit_model(SubjectVisit):
                self.assertIsInstance(visit, Visit)

    def test_cannot_add_membership_if_missing_schedule(self):
        self.bad_visit_schedule.add_schedule('schedule')
        self.assertRaises(VisitScheduleError, self.bad_visit_schedule.add_membership_form, 'schedule1000')

    def test_cannot_add_visit_if_missing_schedule(self):
        self.bad_visit_schedule.add_schedule('schedule')
        self.assertRaises(VisitScheduleError, self.bad_visit_schedule.add_visit, 'schedule1000', '10000', SubjectVisit)

    def test_schedule_already_registered(self):
        self.bad_visit_schedule.add_schedule('schedule')
        self.assertRaises(AlreadyRegistered, self.bad_visit_schedule.add_schedule, 'schedule')

    def test_membership_form_already_registered(self):
        self.bad_visit_schedule.add_schedule('schedule')
        self.bad_visit_schedule.add_membership_form('schedule', model=SubjectConsent)
        self.assertRaises(AlreadyRegistered, self.bad_visit_schedule.add_membership_form, 'schedule', model=SubjectConsent)

    def test_visit_already_registered_with_schedule(self):
        self.bad_visit_schedule.add_schedule('schedule')
        self.bad_visit_schedule.add_membership_form('schedule', model=SubjectConsent)
        self.bad_visit_schedule.add_visit('schedule', '1000', visit_model=SubjectVisit)
        self.assertRaises(AlreadyRegistered, self.bad_visit_schedule.add_visit, 'schedule', '1000', visit_model=SubjectVisit)

    def test_add_visit_detects_not_a_visit_model(self):
        self.bad_visit_schedule.add_schedule('schedule')
        self.bad_visit_schedule.add_membership_form('schedule', model=SubjectConsent)
        self.assertRaises(VisitError, self.bad_visit_schedule.add_visit, 'schedule', '1000', visit_model=SubjectConsent)

    def test_schedule_detects_duplicate_timepoint(self):
        self.bad_visit_schedule.add_schedule('schedule')
        self.bad_visit_schedule.add_membership_form('schedule', model=SubjectConsent)
        self.bad_visit_schedule.add_visit('schedule', '1000',
                                          visit_model=SubjectVisit, time_point=0)
        self.assertRaises(ScheduleError, self.bad_visit_schedule.add_visit, 'schedule', '2000',
                          visit_model=SubjectVisit, time_point=0, base_interval=1)

    def test_schedule_detects_duplicate_base_interval(self):
        self.bad_visit_schedule.add_schedule('schedule')
        self.bad_visit_schedule.add_membership_form('schedule', model=SubjectConsent)
        self.bad_visit_schedule.add_visit('schedule', '1000',
                                          visit_model=SubjectVisit, time_point=0, base_interval=0)
        self.assertRaises(ScheduleError, self.bad_visit_schedule.add_visit, 'schedule', '2000',
                          visit_model=SubjectVisit, time_point=1, base_interval=0)

    def test_gets_previous_visit(self):
        schedule_name = 'schedule'
        self.bad_visit_schedule.add_schedule('schedule')
        self.bad_visit_schedule.add_membership_form('schedule', model=SubjectConsent)
        self.bad_visit_schedule.add_visit(schedule_name, '1000',
                                          visit_model=SubjectVisit, time_point=0)
        self.bad_visit_schedule.add_visit(schedule_name, '1010',
                                          visit_model=SubjectVisit, time_point=1, base_interval=1)
        visit = self.bad_visit_schedule.add_visit(schedule_name, '1020',
                                                  visit_model=SubjectVisit, time_point=2, base_interval=2)
        self.bad_visit_schedule.add_visit(schedule_name, '1030',
                                          visit_model=SubjectVisit, time_point=3, base_interval=3)
        self.bad_visit_schedule.add_visit(schedule_name, '1040',
                                          visit_model=SubjectVisit, time_point=4, base_interval=4)
        schedule = self.bad_visit_schedule.schedules.get(schedule_name)
        self.assertEquals(schedule.get_previous_visit('1030'), visit)

    def test_gets_ordered_visits(self):
        schedule_name = 'schedule'
        self.bad_visit_schedule.add_schedule('schedule')
        self.bad_visit_schedule.add_membership_form('schedule', model=SubjectConsent)
        self.bad_visit_schedule.add_visit(schedule_name, '1000',
                                          visit_model=SubjectVisit, time_point=0)
        self.bad_visit_schedule.add_visit(schedule_name, '1010',
                                          visit_model=SubjectVisit, time_point=1, base_interval=1)
        self.bad_visit_schedule.add_visit(schedule_name, '1020',
                                          visit_model=SubjectVisit, time_point=2, base_interval=2)
        self.bad_visit_schedule.add_visit(schedule_name, '1030',
                                          visit_model=SubjectVisit, time_point=3, base_interval=3)
        self.bad_visit_schedule.add_visit(schedule_name, '1040',
                                          visit_model=SubjectVisit, time_point=4, base_interval=4)
        schedule = self.bad_visit_schedule.schedules.get(schedule_name)
        self.assertEquals([x.time_point for x in schedule.ordered_visits], [0, 1, 2, 3, 4])

    def test_crfs_unique_show_order(self):
        crfs = (
            Crf(show_order=10, app_label='example', model_name='CrfOne'),
            Crf(show_order=20, app_label='example', model_name='CrfTwo'),
            Crf(show_order=20, app_label='example', model_name='CrfThree'),
        )
        schedule_name = 'schedule'
        self.bad_visit_schedule.add_schedule('schedule')
        self.bad_visit_schedule.add_membership_form('schedule', model=SubjectConsent)
        self.assertRaises(CrfError, self.bad_visit_schedule.add_visit, schedule_name, '1000',
                          visit_model=SubjectVisit, time_point=0, crfs=crfs)
