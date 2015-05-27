from django.test import TestCase
from edc.device.device.classes import Device
from edc.testing.models import TestRequisition


class RequisitionMethodsTest(TestCase):

    def test_prepare_requisition_identifier(self):
        mm = '02'
        yy = '13'
        x = 0
        device = Device()
        requisition = TestRequisition()
#        lst = []
#        while x < 10001:
#            lst.append(requisition.prepare_requisition_identifier(device_id='12'))
#            x += 1
#            #self.assertEqual(requisition.prepare_requisition_identifier(device_id='99'), '99MR7HX')
#        #identifier = Identifier(identifier_type='subject', site_code='99', month=mm, year=yy)
#        #self.assertEqual(identifier.create(), '1MYDBZ')
#        print len(lst)
#        print len(set(lst))
#        self.assertEqual(len(lst), 10001)
#        self.assertEqual(len(set(lst)), 10001, msg='list of identifiers is not unique after {0} identifiers'.format(len(set(lst))))
#        print lst
        lst = []
        
        print 'WARNING: Requisition identifier tests are DISABLED!'
#         print 'creating ALOT of identifiers ...this will take a while!'
#         while x < 10001:
#             identifier = Identifier(identifier_type='subject', counter_length=1, month=mm, year=yy)
#             lst.append(identifier.create())
#             x += 1
#         print x
#         print lst
#         self.assertEqual(len(lst), 10001)
#         self.assertEqual(len(set(lst)), 10001, msg='list of identifiers is not unique')
