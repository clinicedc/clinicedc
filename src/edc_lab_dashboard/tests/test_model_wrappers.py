from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_lab.models import Aliquot, Box, BoxType, Manifest, Shipper, Consignee
from edc_lab.models import ManifestItem

from ..model_wrappers import AliquotModelWrapper, BoxModelWrapper, ManageBoxItemModelWrapper
from ..model_wrappers import ManifestItemModelWrapper, ManifestModelWrapper
# from ..model_wrappers import RequisitionModelWrapper


app_config = django_apps.get_app_config('edc_lab_dashboard')


class TestModelWrapper(TestCase):

    def test_aliquot_model_wrapper(self):
        wrapper_cls = AliquotModelWrapper
        next_url_name = wrapper_cls.next_url_name
        wrapper_cls.next_url_name = next_url_name.split(':')[1]
        obj = Aliquot.objects.create(count=0)
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href, f'/admin/edc_lab/aliquot/{obj.id}/change/?next=aliquot_listboard_url&')
        self.assertEqual(wrapper.reverse(), '/listboard/aliquot/')

    def test_box_model_wrapper(self):
        wrapper_cls = BoxModelWrapper
        next_url_name = wrapper_cls.next_url_name
        wrapper_cls.next_url_name = next_url_name.split(':')[1]
        box_type = BoxType.objects.create(across=9, down=9, total=81)
        obj = Box.objects.create(
            box_identifier='1234',
            box_type=box_type)
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href, f'/admin/edc_lab/box/{obj.id}/change/?next=pack_listboard_url&')
        self.assertEqual(wrapper.reverse(), '/listboard/pack/')

    def test_manage_box_item_model_wrapper(self):
        wrapper_cls = ManageBoxItemModelWrapper
        next_url_name = wrapper_cls.next_url_name
        wrapper_cls.next_url_name = next_url_name.split(':')[1]
        box_type = BoxType.objects.create(across=9, down=9, total=81)
        box_identifier = '1234'
        obj = Box.objects.create(
            box_identifier=box_identifier,
            box_type=box_type)
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href,
            f'/admin/edc_lab/box/{obj.id}/change/?next=manage_box_listboard_url,'
            f'box_identifier,action_name&box_identifier={box_identifier}&action_name=manage&')
        # self.assertEqual(wrapper.reverse(), '/listboard/pack/')

    def test_manifest_item_model_wrapper(self):
        wrapper_cls = ManifestItemModelWrapper
        next_url_name = wrapper_cls.next_url_name
        wrapper_cls.next_url_name = next_url_name.split(':')[1]
        manifest = Manifest.objects.create(
            site_code='1',
            site_name='name',
            consignee=Consignee.objects.create(name='name'),
            shipper=Shipper.objects.create(name='name'))
        obj = ManifestItem.objects.create(
            manifest=manifest)
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href, f'/admin/edc_lab/manifestitem/{obj.id}/change/?next=manage_manifest_listboard_url&')
        # self.assertEqual(wrapper.reverse(), '/listboard/pack/')

    def test_manifest_model_wrapper(self):
        wrapper_cls = ManifestModelWrapper
        next_url_name = wrapper_cls.next_url_name
        wrapper_cls.next_url_name = next_url_name.split(':')[1]
        obj = Manifest.objects.create(
            site_code='1',
            site_name='name',
            consignee=Consignee.objects.create(name='name'),
            shipper=Shipper.objects.create(name='name'))
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href, f'/admin/edc_lab/manifest/{obj.id}/change/?next=manifest_listboard_url&')
        self.assertEqual(wrapper.reverse(), '/listboard/manifest/')

#     def test_requisition_model_wrapper(self):
#         wrapper_cls = RequisitionModelWrapper
#         next_url_name = wrapper_cls.next_url_name
#         wrapper_cls.next_url_name = next_url_name.split(':')[1]
#         box_type = BoxType.objects.create(across=9, down=9, total=81)
#         obj = Requisition.objects.create(
#             box_identifier='1234',
#             box_type=box_type)
#         wrapper = wrapper_cls(obj)
#         self.assertEqual(
#             wrapper.href, f'/admin/edc_lab/requisition/{obj.id}/change/?next=requisition_listboard_url&')
#         self.assertEqual(wrapper.reverse(), '/listboard/requisition/')
