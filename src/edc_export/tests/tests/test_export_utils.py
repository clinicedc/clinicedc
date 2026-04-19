from django.core.management import CommandError
from django.test import SimpleTestCase, tag

from edc_export.utils import (
    get_default_models_for_export,
    get_model_names_for_export,
)


@tag("export")
class TestGetDefaultModelsForExport(SimpleTestCase):
    def test_unknown_trial_prefix_raises(self):
        """A typo in trial_prefix should raise CommandError, not
        silently return only the six generic framework models.
        """
        with self.assertRaises(CommandError) as cm:
            get_default_models_for_export("no_such_trial_prefix_xyz")
        msg = str(cm.exception)
        self.assertIn("no_such_trial_prefix_xyz", msg)
        self.assertIn("No installed app matched", msg)
        # error lists all expected app suffixes so operator can see
        # which patterns were attempted
        for suffix in (
            "_consent",
            "_lists",
            "_subject",
            "_ae",
            "_prn",
            "_screening",
        ):
            self.assertIn(suffix, msg)


@tag("export")
class TestGetModelNamesForExport(SimpleTestCase):
    def test_unknown_app_label_raises(self):
        with self.assertRaises(CommandError) as cm:
            get_model_names_for_export(
                app_labels=["no_such_app_xyz"], model_names=None
            )
        self.assertIn("no_such_app_xyz", str(cm.exception))
        self.assertIn("unknown app_label", str(cm.exception))

    def test_unknown_model_name_raises(self):
        with self.assertRaises(CommandError) as cm:
            get_model_names_for_export(
                app_labels=None, model_names=["edc_export.no_such_model"]
            )
        self.assertIn("edc_export.no_such_model", str(cm.exception))
        self.assertIn("unknown model", str(cm.exception))

    def test_collects_all_errors_in_single_raise(self):
        """All invalid labels and model names should be reported
        together, not one per re-run.
        """
        with self.assertRaises(CommandError) as cm:
            get_model_names_for_export(
                app_labels=["bogus_app_1", "bogus_app_2"],
                model_names=["bogus.one", "bogus.two"],
            )
        msg = str(cm.exception)
        self.assertIn("bogus_app_1", msg)
        self.assertIn("bogus_app_2", msg)
        self.assertIn("bogus.one", msg)
        self.assertIn("bogus.two", msg)

    def test_malformed_model_name_raises(self):
        """Values that can't be parsed as `app_label.ModelName` raise
        ValueError inside get_model(); we coerce that to CommandError.
        """
        with self.assertRaises(CommandError) as cm:
            get_model_names_for_export(
                app_labels=None, model_names=["not_a_valid_label"]
            )
        self.assertIn("not_a_valid_label", str(cm.exception))

    def test_valid_app_label_returns_models(self):
        result = get_model_names_for_export(
            app_labels=["edc_export"], model_names=None
        )
        self.assertTrue(len(result) > 0)
        # every entry is label_lower format
        for name in result:
            self.assertIn(".", name)

    def test_valid_model_name_passthrough(self):
        result = get_model_names_for_export(
            app_labels=None, model_names=["edc_export.datarequest"]
        )
        self.assertIn("edc_export.datarequest", result)

    def test_none_inputs_return_empty(self):
        self.assertEqual(
            get_model_names_for_export(app_labels=None, model_names=None), []
        )

    def test_deduplicates(self):
        """Same model specified twice -> returned once."""
        result = get_model_names_for_export(
            app_labels=None,
            model_names=["edc_export.datarequest", "edc_export.datarequest"],
        )
        self.assertEqual(result.count("edc_export.datarequest"), 1)
