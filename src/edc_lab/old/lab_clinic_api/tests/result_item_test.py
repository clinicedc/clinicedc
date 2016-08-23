'''
Created on Oct 19, 2012

@author: sirone
'''
from django.db.models.loading import get_model
from edc_registration.models import RegisteredSubject

from django.test import TestCase

from .test_case_data import (
    TRUE_G1_ASSERTIONS, FALSE_G1_ASSERTIONS, TRUE_G2_ASSERTIONS, FALSE_G2_ASSERTIONS,
    TRUE_G3_ASSERTIONS, FALSE_G3_ASSERTIONS, TRUE_G4_ASSERTIONS, FALSE_G4_ASSERTIONS)


class ResultItemTestCase(TestCase):

    def test_Haemaglobin_grade_flag(self):
            for flag_args in TRUE_G1_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertTrue(
                    grade == 1, "TRUE_G1 " + str(flag_args['result_value']) + " FAILED. Returned Grade=" + str(grade))
            for flag_args in FALSE_G1_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertFalse(
                    grade == 1, "FALSE_G1 " + str(flag_args['result_value']) + " FAILED. Returned Grade=" + str(grade))
            for flag_args in TRUE_G2_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertTrue(
                    grade == 2, "TRUE_G2 " + str(flag_args['result_value']) + " FAILED. Returned Grade=" + str(grade))
            for flag_args in FALSE_G2_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertFalse(
                    grade == 2, "FALSE_G2 " + str(flag_args['result_value']) + " FAILED. Returned Grade=" + str(grade))
            for flag_args in TRUE_G3_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertTrue(
                    grade == 3, "TRUE_G3 " + str(flag_args['result_value']) + " FAILED. Returned Grade=" + str(grade))
            for flag_args in FALSE_G3_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertFalse(
                    grade == 3, "FALSE_G3 " + str(flag_args['result_value']) + " FAILED. Returned Grade=" + str(grade))
            for flag_args in TRUE_G4_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertTrue(
                    grade == 4, "TRUE_G4 " + str(flag_args['result_value']) + " FAILED. Returned Grade=" + str(grade))
            for flag_args in FALSE_G4_ASSERTIONS:
                grade = self.get_result_item_flag(flag_args)
                self.assertFalse(
                    grade == 4, "FALSE_G4 " + str(flag_args['result_value']) + " FAILED. Returned Grade=" + str(grade))

    def get_result_item_flag(self, flag_args):
        resultitem_class = get_model('lab_clinic_api', 'resultitem')
        result_item = resultitem_class()
        subject = RegisteredSubject()
        testcode_class = get_model('lab_clinic_api', 'testcode')
        test_code = testcode_class.objects.filter(code='HGB')[0]
        result_item.result_item_value_as_float = flag_args['result_value']
        result_item.test_code = test_code
        result_item.result_item_datetime = flag_args['datetime_drawn']
        subject.dob = flag_args['dob']
        subject.gender = flag_args['gender']
        subject.hiv_status = flag_args['hiv_status']
        receive_class = get_model('lab_clinic_api', 'receive')
        receive = receive_class()
        receive.registered_subject = subject
        aliquot_class = get_model('lab_clinic_api', 'aliquot')
        aliquot = aliquot_class()
        aliquot.receive = receive
        order_class = get_model('lab_clinic_api', 'order')
        order = order_class()
        order.aliquot = aliquot
        result_class = get_model('lab_clinic_api', 'result')
        result = result_class()
        result.order = order
        result_item.result = result
        return result_item.grade_flag
