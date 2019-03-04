from faker import Faker

from django.apps import apps as django_apps
from django.test import TestCase, tag

from ..models import IdentifierModel
from ..subject_identifier import SubjectIdentifier
from ..infant_identifier import InfantIdentifier
from django.test.utils import override_settings
from django.contrib.sites.models import Site
from edc_registration.models import RegisteredSubject

fake = Faker()


class TestInfantIdentifier(TestCase):
    def get_maternal_identifier(self):
        site = Site.objects.get_current()
        maternal_identifier = SubjectIdentifier(
            identifier_type="subject",
            requesting_model="edc_identifier.enrollment",
            protocol_number="000",
            site=site,
            device_id="99",
            last_name=fake.last_name(),
        )
        return maternal_identifier

    def test_create_singleton(self):
        maternal_identifier = self.get_maternal_identifier()
        self.assertEqual(maternal_identifier.identifier, "000-40990001-6")
        infant_identifier = InfantIdentifier(
            maternal_identifier=maternal_identifier,
            requesting_model="edc_identifier.maternallabdel",
            birth_order=1,
            live_infants=1,
        )
        self.assertEqual(infant_identifier.identifier, "000-40990001-6-10")

    def test_create_twins(self):
        maternal_identifier = self.get_maternal_identifier()
        infant_identifier1 = InfantIdentifier(
            maternal_identifier=maternal_identifier,
            requesting_model="edc_identifier.maternallabdel",
            birth_order=1,
            live_infants=2,
        )
        infant_identifier2 = InfantIdentifier(
            maternal_identifier=maternal_identifier,
            requesting_model="edc_identifier.maternallabdel",
            birth_order=2,
            live_infants=2,
        )
        self.assertEqual(infant_identifier1.identifier, "000-40990001-6-25")
        self.assertEqual(infant_identifier2.identifier, "000-40990001-6-26")

    @override_settings(SITE_ID=20)
    def test_create_triplets(self):
        Site.objects.create(pk=20)
        maternal_identifier = self.get_maternal_identifier()

        infant_identifier1 = InfantIdentifier(
            maternal_identifier=maternal_identifier,
            requesting_model="edc_identifier.maternallabdel",
            birth_order=1,
            live_infants=3,
        )
        infant_identifier2 = InfantIdentifier(
            maternal_identifier=maternal_identifier,
            requesting_model="edc_identifier.maternallabdel",
            birth_order=2,
            live_infants=3,
        )
        infant_identifier3 = InfantIdentifier(
            maternal_identifier=maternal_identifier,
            requesting_model="edc_identifier.maternallabdel",
            birth_order=3,
            live_infants=3,
        )

        self.assertEqual(infant_identifier1.identifier, "000-20990001-8-36")
        self.assertEqual(infant_identifier2.identifier, "000-20990001-8-37")
        self.assertEqual(infant_identifier3.identifier, "000-20990001-8-38")

        self.assertEqual(
            IdentifierModel.objects.filter(
                identifier_type="infant",
                model="edc_identifier.maternallabdel",
                protocol_number="000",
                site=Site.objects.get_current(),
            ).count(),
            3,
        )

        try:
            RegisteredSubject.objects.get(
                subject_identifier=infant_identifier1.identifier
            )
        except RegisteredSubject.DoesNotExist:
            self.fail("RegisteredSubject.DoesNotExist unexpectedly raised")

        try:
            RegisteredSubject.objects.get(
                subject_identifier=infant_identifier2.identifier
            )
        except RegisteredSubject.DoesNotExist:
            self.fail("RegisteredSubject.DoesNotExist unexpectedly raised")

        try:
            RegisteredSubject.objects.get(
                subject_identifier=infant_identifier3.identifier
            )
        except RegisteredSubject.DoesNotExist:
            self.fail("RegisteredSubject.DoesNotExist unexpectedly raised")

    def test_create_triplets_only_registered_2nd_born(self):
        maternal_identifier = self.get_maternal_identifier()
        infant_identifier = InfantIdentifier(
            maternal_identifier=maternal_identifier,
            requesting_model="edc_identifier.maternallabdel",
            birth_order=2,
            live_infants=3,
        )
        self.assertEqual(infant_identifier.identifier, "000-40990001-6-37")

    def test_create_triplets_only_registered_1st_born(self):
        maternal_identifier = self.get_maternal_identifier()
        infant_identifier = InfantIdentifier(
            maternal_identifier=maternal_identifier,
            requesting_model="edc_identifier.maternallabdel",
            birth_order=1,
            live_infants=3,
        )
        self.assertEqual(infant_identifier.identifier, "000-40990001-6-36")
