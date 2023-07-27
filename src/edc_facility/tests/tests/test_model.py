from django.test import TestCase
from edc_utils import get_utcnow

from edc_facility.models import HealthFacility, HealthFacilityTypes, Holiday


class TestModel(TestCase):
    def test_str(self):
        obj = Holiday.objects.create(
            country="botswana", local_date=get_utcnow().date(), name="holiday"
        )
        self.assertTrue(str(obj))

    def test_str_health_facility(self):
        health_facility_type = HealthFacilityTypes.objects.all()[0]
        obj = HealthFacility.objects.create(
            report_datetime=get_utcnow(),
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
            report_datetime=get_utcnow(),
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
        self.assertEqual(obj.clinic_days, [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(obj.clinic_days_str, "MTWThFSSu")

    def test_health_facility_natural_key(self):
        health_facility_type = HealthFacilityTypes.objects.all()[0]
        obj = HealthFacility.objects.create(
            report_datetime=get_utcnow(),
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
