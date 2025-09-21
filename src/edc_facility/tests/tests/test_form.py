from clinicedc_tests.sites import all_sites
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_facility.form_validators import HealthFacilityFormValidator
from edc_facility.forms import HealthFacilityForm
from edc_facility.import_holidays import import_holidays
from edc_facility.models import HealthFacility, HealthFacilityTypes
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("facility")
@override_settings(SITE_ID=10)
class TestForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def test_form_validator_ok(self):
        form_validator = HealthFacilityFormValidator(
            cleaned_data=dict(tue=True, thu=True),
            instance=HealthFacility,
        )
        form_validator.validate()
        self.assertEqual(form_validator._errors, {})

    def test_form_ok(self):
        data = dict()

        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertIn("report_datetime", form._errors)

        data = dict(
            report_datetime=timezone.now(),
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertIn("name", form._errors)

        data = dict(
            report_datetime=timezone.now(),
            name="My Health Facility",
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertIn("health_facility_type", form._errors)

        data = dict(
            report_datetime=timezone.now(),
            name="My Health Facility",
            health_facility_type=HealthFacilityTypes.objects.all()[0],
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertIn("__all__", form._errors)
        self.assertIn("Select at least one clinic day", str(form._errors))

        data = dict(
            report_datetime=timezone.now(),
            name="My Health Facility",
            health_facility_type=HealthFacilityTypes.objects.all()[0],
            tue=True,
            thu=True,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = HealthFacilityForm(data=data, instance=HealthFacility())
        form.is_valid()
        self.assertEqual({}, form._errors)

        form.save()

        try:
            HealthFacility.objects.get(name="MY HEALTH FACILITY")
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")
