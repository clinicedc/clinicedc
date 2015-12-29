from django.test import SimpleTestCase
from django.db.models import get_app, get_models
from django.contrib.auth.models import Group

from edc.lab.lab_profile.classes import site_lab_profiles
from edc.lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc.subject.entry.models import Entry
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.testing.classes import TestAppConfiguration, TestVisitSchedule, TestLabProfile

from ..classes import Permissions
from ..models import VisitDefinition


class TestPermissions(SimpleTestCase):

    def startup(self):
        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass

        TestAppConfiguration().prepare()
        site_lab_tracker.autodiscover()
        TestVisitSchedule().build()

    def test_adds_permissions1(self):
        self.startup()
        permissions = Permissions('field_staff', ['add'], visit_definition_codes=['1000'])
        permissions.replace()
        group = Group.objects.get(name='field_staff')
        self.assertGreater(group.permissions.all().count(), 0)

    def test_adds_permissions2(self):
        """Adds permissions to the group for just add."""
        self.startup()
        permissions = Permissions('field_staff', ['add'], visit_definition_codes=['1000'])
        permissions.clear_permissions_for_group()
        group = Group.objects.get(name='field_staff')
        permissions.replace()
        self.assertGreater(group.permissions.filter(codename__icontains='add_').count(), 0)
        self.assertEqual(group.permissions.filter(codename__icontains='change_').count(), 0)
        self.assertEqual(group.permissions.filter(codename__icontains='delete_').count(), 0)

    def test_adds_permissions3(self):
        """Adds permissions to the group for both add and change."""
        self.startup()
        codes = ['1000']
        visit_definitions = VisitDefinition.objects.filter(code__in=codes)
        entry_count = Entry.objects.filter(visit_definition__in=visit_definitions).count()
        permissions = Permissions('field_staff', ['add', 'change'], visit_definition_codes=codes)
        permissions.replace()
        group = Group.objects.get(name='field_staff')
        self.assertEqual(group.permissions.filter(codename__icontains='add_').count(), entry_count)
        self.assertEqual(group.permissions.filter(codename__icontains='change_').count(), entry_count)
        self.assertEqual(group.permissions.filter(codename__icontains='delete_').count(), 0)

    def test_adds_permissions4(self):
        """Adds permissions for visit 1000 to the group for add and change, delete."""
        self.startup()
        codes = ['1000']
        visit_definitions = VisitDefinition.objects.filter(code__in=codes)
        entry_count = Entry.objects.filter(visit_definition__in=visit_definitions).count()
        permissions = Permissions('field_staff', ['add', 'change', 'delete'], visit_definition_codes=codes)
        permissions.replace()
        group = Group.objects.get(name='field_staff')
        self.assertEqual(group.permissions.filter(codename__icontains='add_').count(), entry_count)
        self.assertEqual(group.permissions.filter(codename__icontains='change_').count(), entry_count)
        self.assertEqual(group.permissions.filter(codename__icontains='delete_').count(), entry_count)

    def test_adds_permissions5(self):
        """Adds permissions for another visit, 2000, for add, change and delete."""
        self.startup()
        codes = ['2000']
        visit_definitions = VisitDefinition.objects.filter(code__in=codes)
        entry_count = Entry.objects.filter(visit_definition__in=visit_definitions).count()
        permissions = Permissions('field_staff', ['add', 'change', 'delete'], visit_definition_codes=codes)
        permissions.replace()
        group = Group.objects.get(name='field_staff')
        self.assertEqual(group.permissions.filter(codename__icontains='add_').count(), entry_count)
        self.assertEqual(group.permissions.filter(codename__icontains='change_').count(), entry_count)
        self.assertEqual(group.permissions.filter(codename__icontains='delete_').count(), entry_count)

    def test_adds_permissions6(self):
        """Adds permissions for both visits, 1000 and 2000, to the group for both add and change and delete and does not duplicate."""
        self.startup()
        codes = ['1000', '2000']
        visit_definitions = VisitDefinition.objects.filter(code__in=codes)
        entries = Entry.objects.filter(visit_definition__in=visit_definitions)
        entry_count = len(list(set([entry.content_type_map.content_type_id for entry in entries])))
        permissions = Permissions('field_staff', ['add', 'change', 'delete'], visit_definition_codes=codes)
        permissions.replace()
        group = Group.objects.get(name='field_staff')
        self.assertEqual(group.permissions.filter(codename__icontains='add_').count(), entry_count)
        self.assertEqual(group.permissions.filter(codename__icontains='change_').count(), entry_count)
        self.assertEqual(group.permissions.filter(codename__icontains='delete_').count(), entry_count)

    def test_adds_permissions7(self):
        """Creates a group if it does not exist."""
        self.startup()
        codes = ['1000']
        permissions = Permissions('field_staff_team', ['add'], visit_definition_codes=codes)
        permissions.replace()
        group = Group.objects.get(name='field_staff_team')
        self.assertGreater(group.permissions.all().count(), 0)

    def test_adds_permissions8(self):
        """Adds permissions for all models in the app"""
        self.startup()
        permissions = Permissions('field_staff_team', ['add'], app_label='testing')
        permissions.replace()
        group = Group.objects.get(name='field_staff_team')
        app = get_app('testing')
        models = get_models(app)
        self.assertEquals(group.permissions.all().count(), len(models))

    def test_adds_permissions9(self):
        """Adds permissions for specified list of models in the app."""
        self.startup()
        group = Group.objects.get(name='field_staff_team')
        permissions = Permissions('field_staff', ['add', 'change'], app_label='testing', models=['testvisit', 'TestScheduledModel'])
        permissions.replace()
        self.assertEqual(group.permissions.filter(codename='add_testvisit').count(), 1)
        self.assertEqual(group.permissions.filter(codename='add_testscheduledmodel').count(), 1)
        self.assertEqual(group.permissions.filter(codename='change_testvisit').count(), 1)
        self.assertEqual(group.permissions.filter(codename='change_testscheduledmodel').count(), 1)

    def test_adds_permissions10(self):
        """Raises error if model not in app"""
        self.startup()
        self.assertRaises(AttributeError, Permissions, 'field_staff', ['add', 'change'], app_label='testing', models=['testvisit', 'BadDogModel'])
