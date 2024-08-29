import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from django.db import OperationalError, connection
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_appointment_app.models import CrfOne, Panel, SubjectRequisition, SubjectVisit
from edc_appointment_app.tests import AppointmentAppTestCaseMixin
from edc_auth.get_app_codenames import get_app_codenames
from edc_constants.constants import YES
from edc_lab_panel.constants import FBC
from edc_reportable import TEN_X_9_PER_LITER

from edc_qareports.sql_generator import CrfCase, CrfCaseError, RequisitionCase
from edc_qareports.sql_generator.crf_subquery import CrfSubqueryError

from ..models import BloodResultsFbc

utc_tz = ZoneInfo("UTC")


@override_settings(SITE_ID=10)
@time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestQA(AppointmentAppTestCaseMixin, TestCase):
    helper_cls = Helper

    def create_unscheduled_appointments(self, appointment):
        pass

    def test_codenames(self):
        """Assert default codenames.

        Note: in tests this will include codenames for test models.
        """
        codenames = get_app_codenames("edc_qareports")
        codenames.sort()
        expected_codenames = [
            "edc_qareports.add_bloodresultsfbc",
            "edc_qareports.add_edcpermissions",
            "edc_qareports.add_note",
            "edc_qareports.change_bloodresultsfbc",
            "edc_qareports.change_edcpermissions",
            "edc_qareports.change_note",
            "edc_qareports.delete_bloodresultsfbc",
            "edc_qareports.delete_edcpermissions",
            "edc_qareports.delete_note",
            "edc_qareports.view_bloodresultsfbc",
            "edc_qareports.view_edcpermissions",
            "edc_qareports.view_note",
            "edc_qareports.view_qareportlog",
            "edc_qareports.view_qareportlogsummary",
        ]
        self.assertEqual(codenames, expected_codenames)

    def test_crfcase_invalid(self):
        crf_case = CrfCase()
        # sql template requires a complete dictionary of values
        self.assertRaises(CrfSubqueryError, getattr, crf_case, "sql")

    def test_fldname_crfcase(self):
        """Assert generates valid SQL or raises"""
        # raise for bad fld_name
        crf_case = CrfCase(
            label="F1 is missing",
            dbtable="edc_appointment_app_crfone",
            label_lower="edc_appointment_app.crfone",
            fld_name="bad_fld_name",
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(crf_case.sql)
        except OperationalError as e:
            self.assertIn("bad_fld_name", str(e))
        else:
            self.fail("OperationalError not raised for invalid fld_name.")

        # ok
        crf_case = CrfCase(
            label="F1 is missing",
            dbtable="edc_appointment_app_crfone",
            label_lower="edc_appointment_app.crfone",
            fld_name="f1",
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(crf_case.sql)
        except OperationalError as e:
            self.fail(f"OperationalError unexpectedly raised, Got {e}.")

    def test_where_instead_of_fldname_crfcase(self):
        """Assert generates valid SQL or raises"""
        # raise for bad fld_name
        crf_case = CrfCase(
            label="No F1 when F2 is YES",
            dbtable="edc_appointment_app_crfone",
            label_lower="edc_appointment_app.crfone",
            where="bad_fld_name is null and f2='Yes'",
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(crf_case.sql)
        except OperationalError as e:
            self.assertIn("bad_fld_name", str(e))
        else:
            self.fail("OperationalError not raised for invalid fld_name.")

        # ok
        crf_case = CrfCase(
            label="No F1 when F2 is YES",
            dbtable="edc_appointment_app_crfone",
            label_lower="edc_appointment_app.crfone",
            where="f1 is null and f2='Yes'",
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(crf_case.sql)
        except OperationalError as e:
            self.fail(f"OperationalError unexpectedly raised, Got {e}.")

    def test_subquery_crfcase(self):
        crf_case = CrfCase(
            label="No F1 when F2 is YES",
            dbtable="edc_appointment_app_crfone",
            label_lower="edc_appointment_app.crfone",
            where="f1 is null and f2='Yes'",
        )
        try:
            crf_case.fetchall()
        except CrfCaseError as e:
            self.fail(f"CrfCaseError unexpectedly raised, Got {e}.")

    def test_subquery_with_recs_crfcase(self):
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)
        subject_visit = SubjectVisit.objects.get(appointment=appointment)
        CrfOne.objects.create(subject_visit=subject_visit, f1=None, f2=YES)
        crf_case = CrfCase(
            label="No F1 when F2 is YES",
            dbtable="edc_appointment_app_crfone",
            label_lower="edc_appointment_app.crfone",
            where="f1 is null and f2='Yes'",
        )
        try:
            rows = crf_case.fetchall()
        except CrfCaseError as e:
            self.fail(f"CrfCaseError unexpectedly raised, Got {e}.")
        self.assertEqual(len(rows), 1)

    def test_requisition_case(self):
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)
        subject_visit = SubjectVisit.objects.get(appointment=appointment)
        panel = Panel.objects.create(name=FBC)
        subject_requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit, is_drawn=YES, panel=panel
        )
        # need to pass table names explicitly since app_name for
        # BloodResultsFbc CRF is not the same as subject_visit and
        # subject_requisition. Normally the defaults are correct.
        requisition_case = RequisitionCase(
            label="FBC Requisition, no results",
            dbtable="edc_qareports_bloodresultsfbc",
            label_lower="edc_qareports.bloodresultsfbc",
            panel=FBC,
            subjectvisit_dbtable="edc_appointment_app_subjectvisit",
            subjectrequisition_dbtable="edc_appointment_app_subjectrequisition",
            panel_dbtable="edc_appointment_app_panel",
        )
        try:
            rows = requisition_case.fetchall()
        except CrfCaseError as e:
            self.fail(f"CrfCaseError unexpectedly raised, Got {e}.")
        self.assertEqual(len(rows), 1)

        # add the result CRF
        BloodResultsFbc.objects.create(
            subject_visit=subject_visit,
            requisition=subject_requisition,
            wbc_value=10.0,
            wbc_units=TEN_X_9_PER_LITER,
            site_id=10,
        )
        try:
            rows = requisition_case.fetchall()
        except CrfCaseError as e:
            self.fail(f"CrfCaseError unexpectedly raised, Got {e}.")
        self.assertEqual(len(rows), 0)
