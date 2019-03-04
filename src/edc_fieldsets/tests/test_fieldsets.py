from django.contrib.admin.utils import flatten_fieldsets
from django.test import TestCase, tag

from ..fieldsets import Fieldsets, FieldsetError
from ..fieldset import Fieldset
from .admin import MyModelAdmin


class TestFieldsets(TestCase):
    def setUp(self):
        self.fieldsets = (
            (
                None,
                {
                    "fields": (
                        "subject_visit",
                        "first_positive",
                        "medical_care",
                        "no_medical_care",
                        "no_medical_care_other",
                        "ever_recommended_arv",
                        "ever_taken_arv",
                        "why_no_arv",
                        "why_no_arv_other",
                        "first_arv",
                        "on_arv",
                        "arv_evidence",
                        "clinic_receiving_from",
                        "next_appointment_date",
                        "arv_stop_date",
                        "arv_stop",
                        "arv_stop_other",
                        "adherence_4_day",
                        "adherence_4_wk",
                    )
                },
            ),
        )
        self.original_fields = (
            "subject_visit",
            "first_positive",
            "medical_care",
            "no_medical_care",
            "no_medical_care_other",
            "ever_recommended_arv",
            "ever_taken_arv",
            "why_no_arv",
            "why_no_arv_other",
            "first_arv",
            "on_arv",
            "arv_evidence",
            "clinic_receiving_from",
            "next_appointment_date",
            "arv_stop_date",
            "arv_stop",
            "arv_stop_other",
            "adherence_4_day",
            "adherence_4_wk",
        )

    def test_fieldset(self):
        """Asserts returns fieldset in original format.
        """
        fs = Fieldsets(self.fieldsets)
        self.assertEqual(fs.fieldsets, self.fieldsets)

    def test_add_fieldset(self):
        """Asserts returns fieldset with added fields.
        """
        fs = Fieldsets(self.fieldsets)
        fs.add_fieldset(
            section="Hospitalisation", fields=("field1", "field2", "field3")
        )
        flatten = flatten_fieldsets(fs.fieldsets)
        self.assertEqual(flatten[-3:], ["field1", "field2", "field3"])

    def test_add_fieldset2(self):
        """Asserts creates sections.
        """
        fs = Fieldsets(self.fieldsets)
        fs.add_fieldset("Hospitalisation", ("field1", "field2", "field3"))
        self.assertEqual(fs.fieldsets[0][0], None)
        self.assertEqual(fs.fieldsets[1][0], "Hospitalisation")

    def test_adds_fieldset_section(self):
        """Asserts adds fields to a new section.
        """
        fs = Fieldsets(self.fieldsets)
        fs.add_fieldset("Hospitalisation", ("field1", "field2", "field3"))
        self.assertEqual(fs.fieldsets[0][1]["fields"], self.original_fields)
        self.assertEqual(fs.fieldsets[1][1]["fields"], ("field1", "field2", "field3"))

    def test_adds_fieldset_section_with_fieldset(self):
        """Asserts adds fields to a new section.
        """
        fieldsets = Fieldsets(self.fieldsets)
        fieldset = Fieldset("field1", "field2", "field3", section="Hospitalisation")
        fieldsets.add_fieldset(fieldset=fieldset)
        self.assertEqual(fieldsets.fieldsets[0][1]["fields"], self.original_fields)
        self.assertEqual(
            fieldsets.fieldsets[1][1]["fields"], ("field1", "field2", "field3")
        )

    def test_insert_insert_after(self):
        """Asserts adds fields to an existing section.
        """
        fs = Fieldsets(self.fieldsets)
        fields = ("field1", "field2", "field3")
        fs.insert_fields(*fields, insert_after="on_arv")
        pos = self.original_fields.index("on_arv")
        self.assertEqual(
            fs.fieldsets[0][1]["fields"][0:pos], self.original_fields[0:pos]
        )
        self.assertEqual(fs.fieldsets[0][1]["fields"][pos + 1 :][0:3], fields)

    def test_insert_fields_after_bad_section(self):
        """Asserts raises if section does not exist.
        """
        fs = Fieldsets(self.fieldsets)
        fields = ("field1", "field2", "field3")
        self.assertRaises(
            FieldsetError,
            fs.insert_fields,
            *fields,
            insert_after="on_arv",
            section="Hospitalization"
        )

    def test_remove_fields(self):
        """Asserts removes fields from an existing section.
        """
        fs = Fieldsets(self.fieldsets)
        fields = ("ever_taken_arv", "why_no_arv", "why_no_arv_other")
        fs.remove_fields(*fields, section=None)
        self.assertTrue(fields[0] not in fs.fieldsets[0][1]["fields"])
        self.assertTrue(fields[1] not in fs.fieldsets[0][1]["fields"])
        self.assertTrue(fields[2] not in fs.fieldsets[0][1]["fields"])

    def test_add_fieldsets(self):
        fieldsets = Fieldsets(MyModelAdmin.fieldsets)
        new_fieldset = Fieldset("field1", "field2", "field3", section="Hospitalisation")
        fieldsets.add_fieldsets(fieldsets=[new_fieldset])
        fieldsets = fieldsets.fieldsets
        self.assertEqual(fieldsets[2], new_fieldset.fieldset)
