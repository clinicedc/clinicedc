from django.test import TestCase
from edc_auth.get_app_codenames import get_app_codenames


class TestQA(TestCase):

    def test_codenames(self):
        codenames = get_app_codenames("edc_qareports")
        codenames.sort()
        expected_codenames = [
            "edc_qareports.add_edcpermissions",
            "edc_qareports.add_note",
            "edc_qareports.change_edcpermissions",
            "edc_qareports.change_note",
            "edc_qareports.delete_edcpermissions",
            "edc_qareports.delete_note",
            "edc_qareports.export_note",
            "edc_qareports.export_qareportlog",
            "edc_qareports.export_qareportlogsummary",
            "edc_qareports.import_note",
            "edc_qareports.view_edcpermissions",
            "edc_qareports.view_note",
            "edc_qareports.view_qareportlog",
            "edc_qareports.view_qareportlogsummary",
            "edc_qareports.viewallsites_note",
            "edc_qareports.viewallsites_qareportlog",
            "edc_qareports.viewallsites_qareportlogsummary",
        ]
        self.assertEqual(codenames, expected_codenames)
