from django.test import TestCase

from edc_dashboard.subject import RegisteredSubjectDashboard


class DropDownListRequisitionsTests(TestCase):

    def test_drop_down_list_requisitions(self):
        rs_dash = RegisteredSubjectDashboard()
        requisitions = [{'status': 'NOT_REQUIRED'},
                        {'status': 'NEW'}, {'status': 'KEYED'}, {'status': 'NOT_REQUIRED'}]
        drop_down_reqs = rs_dash.drop_down_list_requisitions(requisitions)
        self.assertEqual(len(drop_down_reqs), 2, "Drop down reqs should have two (2) listed requisitions")
