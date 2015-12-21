from __future__ import print_function

from datetime import datetime

from django.core.exceptions import ValidationError

from edc_constants.constants import NEW_APPT, COMPLETE_APPT
from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.core.bhp_content_type_map.models import ContentTypeMap
from edc.core.bhp_variables.tests.factories import StudySpecificFactory, StudySiteFactory
from edc.entry_meta_data.models import ScheduledEntryMetaData
from edc.subject.entry.tests.factories import EntryFactory
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.subject.registration.models import RegisteredSubject
from edc.subject.visit_schedule.models import VisitDefinition
from edc.subject.visit_schedule.tests.factories import (
    MembershipFormFactory, ScheduleGroupFactory, VisitDefinitionFactory)
from edc.testing.models import TestConsent, TestScheduledModel

from ..choices import APPT_STATUS
from ..models import Appointment

from .base_appointment_tests import BaseAppointmentTests


class AppointmentMethodTests(BaseAppointmentTests):

    def test_save(self):
        # create an appointment
        self.setup()
        # confirm visit_instance is 0 for first appointment
        self.assertEqual(self.appointment.visit_instance, '0')
        # try to change the visit instnce of the existing appointment to 1
        self.appointment.visit_instance = '1'
        # expect a validation error, because there is no appt with visit_instance == 0
        self.assertRaises(ValidationError, self.appointment.save)
        # put visit_instance back to 0
        self.appointment.visit_instance = '0'
        try:
            self.appointment.save()
        except:
            self.fail('appointment.save() has unexpectedly raised an exception.')
        self.assertEqual(self.appointment.visit_instance, '0')
        # create another appt with the same visit definition, skip an instance, expect a ValidationError
        self.appointment = Appointment(
            appt_datetime=datetime.today(),
            best_appt_datetime=datetime.today(),
            appt_status=NEW_APPT,
            study_site=None,
            visit_definition=self.visit_definition,
            registered_subject=self.registered_subject,
            visit_instance='2')
        self.assertRaises(ValidationError, self.appointment.save)
        # set visit_instance to 1 and expect it to save without an exception
        self.appointment.visit_instance = '1'
        try:
            self.appointment.save()
        except:
            self.fail('appointment.save() has unexpectedly raised an exception.')

    def test_is_new_appointment(self):
        """
        is_new_appointment() should return False if not "new" and "new" must be listed in the choices tuple.
        """
        site_lab_tracker.autodiscover()
        StudySpecificFactory()
        StudySiteFactory()
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        appointment = Appointment()
        dte = datetime.today()
        appointment.appt_datetime = dte
        self.assertEqual(
            appointment.is_new_appointment(), True,
            'Expected is_new_appointment() to return True for appt_status=\'{0}\'. Got \'{1}\''.format(
                appointment.appt_status, appointment.is_new_appointment()))
        appointment.appt_status = COMPLETE_APPT
        self.assertEqual(
            appointment.is_new_appointment(), False,
            'Expected is_new_appointment() to return False for appt_status=\'{0}\'. Got \'{1}\''.format(
                appointment.appt_status, appointment.is_new_appointment()))
        appointment.appt_status = 'incomplete'
        self.assertEqual(
            appointment.is_new_appointment(), False,
            'Expected is_new_appointment() to return False for appt_status=\'{0}\'. Got \'{1}\''.format(
                appointment.appt_status, appointment.is_new_appointment()))
        appointment.appt_status = 'cancelled'
        self.assertEqual(
            appointment.is_new_appointment(), False,
            'Expected is_new_appointment() to return False for appt_status=\'{0}\'. Got \'{1}\''.format(
                appointment.appt_status, appointment.is_new_appointment()))
        is_found_new = False
        for choice in APPT_STATUS:
            appointment.appt_status = choice[0]
            if appointment.appt_status == NEW_APPT:
                # flag to show "new" exists in tuple
                is_found_new = True
                self.assertEqual(appointment.is_new_appointment(), True)
            else:
                # all other cases return False
                self.assertEqual(appointment.is_new_appointment(), False)
        # test "new" case exists in choices
        self.assertEqual(is_found_new, True)

    def test_validate_appt_status(self):
        # setup visit 1000
        from edc.testing.tests.factories import (
            TestRegistrationFactory, TestVisitFactory, TestConsentFactory, TestScheduledModelFactory)
        app_label = 'bhp_base_test'
        site_lab_tracker.autodiscover()
        StudySpecificFactory()
        StudySiteFactory()
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        print('setup the consent catalogue for app {0}'.format(app_label))
        ContentTypeMap.objects.get(content_type__model=TestConsent._meta.object_name.lower())
        print('setup bhp_visit (1000, 1010, 1020, 1030)')
        content_type_map = ContentTypeMap.objects.get(content_type__model='testregistration')
        visit_tracking_content_type_map = ContentTypeMap.objects.get(content_type__model='testvisit')
        membership_form = MembershipFormFactory(content_type_map=content_type_map)
        schedule_group = ScheduleGroupFactory(
            membership_form=membership_form, group_name='Test Reg', grouping_key='REGISTRATION')
        visit_definition = VisitDefinitionFactory(
            code='1000',
            title='Test Registration 00',
            grouping='test_subject',
            time_point=0,
            base_interval=0,
            base_interval_unit='D',
            visit_tracking_content_type_map=visit_tracking_content_type_map)
        visit_definition.schedule_group.add(schedule_group)
        visit_definition = VisitDefinitionFactory(
            code='1010',
            title='Test Registration 10',
            grouping='test_subject',
            time_point=10,
            base_interval=1,
            base_interval_unit='M',
            visit_tracking_content_type_map=visit_tracking_content_type_map)
        visit_definition.schedule_group.add(schedule_group)
        content_type_map = ContentTypeMap.objects.get(
            content_type__model=TestScheduledModel._meta.object_name.lower())
        EntryFactory(visit_definition=visit_definition,
                     content_type_map=content_type_map)

        visit_definition = VisitDefinitionFactory(
            code='1020', title='Test Registration 20', grouping='test_subject',
            time_point=20,
            base_interval=2,
            base_interval_unit='M',
            visit_tracking_content_type_map=visit_tracking_content_type_map)
        visit_definition.schedule_group.add(schedule_group)
        visit_definition = VisitDefinitionFactory(
            code='1030', title='Test Registration 30', grouping='test_subject',
            time_point=30,
            base_interval=3,
            base_interval_unit='M',
            visit_tracking_content_type_map=visit_tracking_content_type_map)
        visit_definition.schedule_group.add(schedule_group)
        # add consent
        test_consent = TestConsentFactory()
        # add registration
        registered_subject = RegisteredSubject.objects.get(subject_identifier=test_consent.subject_identifier)
        self.assertEquals(Appointment.objects.all().count(), 0)
        print('complete a registration form')
        TestRegistrationFactory(registered_subject=registered_subject)
        print('assert 4 appointments created')
        self.assertEquals(Appointment.objects.all().count(), 4)
        print('assert all set to new')
        for appointment in Appointment.objects.all():
            self.assertEqual(appointment.appt_status, NEW_APPT)
        print('attempt to set appointment status, assert reverts to New or Cancelled when no visit tracking')
        for appt_status in APPT_STATUS:
            appointment.appt_status = appt_status[0]
            appointment.save()
            if appt_status == 'cancelled':
                self.assertIn(appointment.appt_status, ['cancelled'])
            else:
                self.assertIn(appointment.appt_status, [NEW_APPT, 'cancelled'])
            print('    {0} becomes {1}'.format(appt_status[0], appointment.appt_status))
        print('get appointment 1000')
        appointment = Appointment.objects.get(registered_subject=registered_subject, visit_definition__code='1000')
        print('add a visit tracking form for appointment 1000')
        TestVisitFactory(appointment=appointment, reason='scheduled')
        print('confirm appt_status changes to \'in_progress\'')
        self.assertEquals(appointment.appt_status, 'in_progress')
        print('confirm not scheduled entries for visit')
        self.assertEqual(ScheduledEntryMetaData.objects.filter(appointment=appointment).count(), 0)
        print('try changing status')
        for appt_status in APPT_STATUS:
            appointment = Appointment.objects.get(
                registered_subject=registered_subject, visit_definition__code='1000', visit_instance='0')
            print('appointment status is {0}'.format(appointment.appt_status))
            # print 'assert there is only one appointment instance'
            # self.assertEquals(Appointment.objects.all().count(), 1)
            print('    attempt to change to {0}'.format(appt_status[0]))
            appointment.appt_status = appt_status[0]
            print('    save')
            if appt_status[0] == 'cancelled':
                appointment.save()
                print('    assert still in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == NEW_APPT:
                appointment.save()
                print('    assert still in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == 'in_progress':
                appointment.save()
                print('    assert still in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == COMPLETE_APPT:
                appointment.save()
                print('    assert allows change to Done')
                self.assertEquals(appointment.appt_status, COMPLETE_APPT)
            elif appt_status[0] == 'incomplete':
                appointment.save()
                print('    assert changes to Done')
                self.assertEquals(appointment.appt_status, COMPLETE_APPT)
            else:
                raise TypeError()
        print('get appointment 1010, which has entries')
        appointment = Appointment.objects.get(registered_subject=registered_subject, visit_definition__code='1010')
        print('add a visit tracking form for appointment 1010')
        test_visit = TestVisitFactory(appointment=appointment, reason='scheduled')
        print('confirm appt_status changes to \'in_progress\'')
        self.assertEquals(appointment.appt_status, 'in_progress')
        print('confirm not scheduled entries for visit')
        self.assertEqual(ScheduledEntryMetaData.objects.filter(appointment=appointment).count(), 1)
        print('try changing status')
        for appt_status in APPT_STATUS:
            appointment = Appointment.objects.get(
                registered_subject=registered_subject, visit_definition__code='1010', visit_instance='0')
            print('appointment status is {0}'.format(appointment.appt_status))
            # print 'assert there is only one appointment instance'
            # self.assertEquals(Appointment.objects.all().count(), 1)
            print('    attempt to change to {0}'.format(appt_status[0]))
            appointment.appt_status = appt_status[0]
            print('    save')
            if appt_status[0] == 'cancelled':
                appointment.save()
                print('    assert still in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == NEW_APPT:
                appointment.save()
                print('    assert still in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == 'in_progress':
                appointment.save()
                print('    assert still in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == COMPLETE_APPT:
                appointment.save()
                print('    assert change to Incomplete')
                self.assertEquals(appointment.appt_status, 'incomplete')
            elif appt_status[0] == 'incomplete':
                appointment.save()
                print('    assert leaves as incomplete')
                self.assertEquals(appointment.appt_status, 'incomplete')
            else:
                raise TypeError()
        print('add the TestScheduledModel for visit 1010, scheduledentry should be KEYED')
        TestScheduledModelFactory(test_visit=test_visit)
        print('assert is KEYED in ScheduledEntryMetaData')
        ScheduledEntryMetaData.objects.filter(appointment=appointment).update(entry_status='KEYED')
        self.assertEqual(ScheduledEntryMetaData.objects.filter(
            appointment=appointment, entry_status='KEYED').count(), 1)
        print('try changing status')
        for appt_status in APPT_STATUS:
            appointment = Appointment.objects.get(
                registered_subject=registered_subject, visit_definition__code='1010', visit_instance='0')
            print('appointment status is {0}'.format(appointment.appt_status))
            print('    attempt to change to {0}'.format(appt_status[0]))
            appointment.appt_status = appt_status[0]
            print('    save')
            if appt_status[0] == 'cancelled':
                appointment.save()
                print('    assert change to in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == NEW_APPT:
                appointment.save()
                print('    assert change to in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == 'in_progress':
                appointment.save()
                print('    assert still in_progress')
                self.assertEquals(appointment.appt_status, 'in_progress')
            elif appt_status[0] == COMPLETE_APPT:
                appointment.save()
                print('    assert still Done')
                self.assertEquals(appointment.appt_status, COMPLETE_APPT)
            elif appt_status[0] == 'incomplete':
                appointment.save()
                print('    assert change to Done')
                self.assertEquals(appointment.appt_status, COMPLETE_APPT)
            else:
                raise TypeError()

    def test_validate_appt_datetime(self):
        self.setup()
        # a new record, original appt_datetime and best_appt_datetime are equal.
        appointment = Appointment()
        dte = datetime.today()
        appointment.appt_datetime = dte
        # returned appt_datetime may not be equal to original appt_datetime
        appt_datetime, appointment.best_appt_datetime = appointment.validate_appt_datetime()
        self.assertEqual(
            appointment.appt_datetime, appointment.best_appt_datetime,
            'Expected appointment.appt_datetime and best_appt_datetime to be equal.')

        # a changed record must return  appt_datetime and best_appt_datetime but they do not need to be equal
        appointment.id = '1'
        appointment.appt_datetime = appt_datetime
        appointment.study_site = None
        appointment.visit_definition = VisitDefinition(code='1000', title='Test')
        appt_datetime, best_appt_datetime = appointment.validate_appt_datetime()
        self.assertIsNotNone(appt_datetime)
        self.assertIsNotNone(best_appt_datetime)
