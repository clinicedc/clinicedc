from clinicedc_tests.sites import all_sites
from django.core.management import CommandError
from django.test import TestCase
from django.test.utils import tag

from edc_export.utils import get_site_ids_for_export
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("export")
class TestGetSiteIdsForExport(TestCase):
    @classmethod
    def setUpTestData(cls):
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def test_site_ids_only_returns_validated_ids(self):
        """Passing `site_ids` only returns those ids after validating
        each against sites.Site."""
        result = get_site_ids_for_export(site_ids=[10, 20, 30], countries=None)
        self.assertEqual(sorted(result), [10, 20, 30])

    def test_site_ids_does_not_duplicate_on_multiple_ids(self):
        """Regression: the previous implementation appended to the
        list being iterated, producing duplicates / infinite loop on
        multi-id input."""
        result = get_site_ids_for_export(site_ids=[10, 20, 30, 40, 50], countries=None)
        self.assertEqual(sorted(result), [10, 20, 30, 40, 50])
        self.assertEqual(len(result), len(set(result)))

    def test_invalid_site_id_raises(self):
        with self.assertRaises(CommandError) as ctx:
            get_site_ids_for_export(site_ids=[99999], countries=None)
        self.assertIn("Invalid site_id", str(ctx.exception))

    def test_countries_only_returns_sites_in_countries(self):
        """Passing `countries` only returns all site ids for those
        countries."""
        result = get_site_ids_for_export(site_ids=None, countries=["botswana"])
        # Botswana sites in clinicedc_tests.sites.all_sites are 10, 20, 30, 40, 50.
        self.assertEqual(sorted(result), [10, 20, 30, 40, 50])

    def test_multiple_countries_unions_site_ids(self):
        result = get_site_ids_for_export(
            site_ids=None, countries=["namibia", "uganda"]
        )
        # namibia=60, uganda=70
        self.assertEqual(sorted(result), [60, 70])

    def test_both_specified_raises(self):
        with self.assertRaises(CommandError) as ctx:
            get_site_ids_for_export(site_ids=[10], countries=["botswana"])
        self.assertIn("not both", str(ctx.exception))

    def test_neither_specified_returns_empty(self):
        """With both inputs empty, returns []. The management command
        is expected to reject this case before calling the helper."""
        self.assertEqual(get_site_ids_for_export(site_ids=None, countries=None), [])
        self.assertEqual(get_site_ids_for_export(site_ids=[], countries=[]), [])
