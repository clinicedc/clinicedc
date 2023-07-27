from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_utils import get_utcnow

from ...form_validators import HealthFacilityFormValidator
from ...forms import HealthFacilityForm
from ...models import HealthFacility, HealthFacilityTypes


class TestForm(TestCase):
    def test_form_validator_ok(self):
        form_validator = HealthFacilityFormValidator(cleaned_data={}, instance=HealthFacility)
        form_validator.validate()
        self.assertEqual(form_validator._errors, {})

    def test_form_ok(self):
        data = dict()

        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertIn("report_datetime", form._errors)

        data = dict(
            report_datetime=get_utcnow(),
        )
        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertIn("name", form._errors)

        data = dict(
            report_datetime=get_utcnow(),
            name="My Health Facility",
        )
        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertIn("health_facility_type", form._errors)

        data = dict(
            report_datetime=get_utcnow(),
            name="My Health Facility",
            health_facility_type=HealthFacilityTypes.objects.all()[0],
        )
        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertEqual({}, form._errors)

        form.save()

        try:
            HealthFacility.objects.get(name="MY HEALTH FACILITY")
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")
