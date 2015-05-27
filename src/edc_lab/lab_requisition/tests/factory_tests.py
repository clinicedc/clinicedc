from django.test import TestCase
# from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
# # from edc.core.bhp_content_type_map.models import ContentTypeMap
# from edc.testing.tests.factories import TestRequisitionFactory
# from lab_clinic_api.tests.factories import AliquotTypeFactory


class FactoryTests(TestCase):

    def setUp(self):
        pass
#         self.study_site = StudySiteFactory(site_code='10', site_name='TEST_SITE')
#         self.study_specific = StudySpecificFactory()
#         content_type_map_helper = ContentTypeMapHelper()
#         content_type_map_helper.populate()
#         content_type_map_helper.sync()
#         # prepare the consent catalogue
#         content_type_map = ContentTypeMap.objects.get(model__iexact=TestSubjectConsent._meta.object_name)
#         consent_catalogue = ConsentCatalogueFactory(content_type_map=content_type_map)
#         content_type_map = ContentTypeMap.objects.get(model__iexact=TestRequisition._meta.object_name)
#         AttachedModelFactory(consent_catalogue=consent_catalogue, content_type_map=content_type_map)

    def test_p1(self):
        print 'NO lab_requisition TESTS'
#         aliquot_type = AliquotTypeFactory()
#         self.assertIsNotNone(TestRequisitionFactory(aliquot_type=aliquot_type))
#         aliquot_type = AliquotTypeFactory()
#         self.assertIsNotNone(TestRequisitionFactory(aliquot_type=aliquot_type))
#         aliquot_type = AliquotTypeFactory()
#         self.assertIsNotNone(TestRequisitionFactory(aliquot_type=aliquot_type))
#         aliquot_type = AliquotTypeFactory()
#         self.assertIsNotNone(TestRequisitionFactory(aliquot_type=aliquot_type))
#         aliquot_type = AliquotTypeFactory()
#         self.assertIsNotNone(TestRequisitionFactory(aliquot_type=aliquot_type))
