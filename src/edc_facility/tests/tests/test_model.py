from clinicedc_tests.sites import all_sites
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_facility.import_holidays import import_holidays
from edc_facility.models import HealthFacility, HealthFacilityTypes, Holiday
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("facility")
@override_settings(SITE_ID=10)
class TestModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def test_str(self):
        obj = Holiday.objects.create(
            country="botswana", local_date=timezone.now().date(), name="holiday"
        )
        self.assertTrue(str(obj))

    def test_str_health_facility(self):
        health_facility_type = HealthFacilityTypes.objects.all()[0]
        obj = HealthFacility.objects.create(
            report_datetime=timezone.now(),
            name="HealthFacility",
            health_facility_type=health_facility_type,
            mon=True,
            tue=True,
            wed=False,
            thu=False,
            fri=False,
            sat=False,
            sun=False,
        )
        self.assertTrue(str(obj))

    def test_health_facility_days(self):
        health_facility_type = HealthFacilityTypes.objects.all()[0]
        obj = HealthFacility.objects.create(
            report_datetime=timezone.now(),
            name="HealthFacility",
            health_facility_type=health_facility_type,
            mon=True,
            tue=True,
            wed=True,
            thu=True,
            fri=True,
            sat=True,
            sun=True,
        )
        self.assertEqual(obj.clinic_days, [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(obj.clinic_days_str, "Mon,Tue,Wed,Thu,Fri,Sat,Sun")

    def test_health_facility_natural_key(self):
        health_facility_type = HealthFacilityTypes.objects.all()[0]
        obj = HealthFacility.objects.create(
            report_datetime=timezone.now(),
            name="HealthFacility",
            health_facility_type=health_facility_type,
            mon=True,
            tue=True,
            wed=True,
            thu=True,
            fri=True,
            sat=True,
            sun=True,
        )
        # assert converted to uppercase in save()
        self.assertEqual(obj.name, "HEALTHFACILITY")
        # retrieve from get_by_natural_key
        obj = HealthFacility.objects.get_by_natural_key(name="HEALTHFACILITY")
        self.assertEqual(obj.name, "HEALTHFACILITY")
        self.assertEqual(obj.natural_key(), ("HEALTHFACILITY",))
