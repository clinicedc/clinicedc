from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_lab.models import Aliquot, Box, BoxType, Manifest, Shipper, Consignee
from edc_lab.models import ManifestItem

from ..model_wrappers import BoxModelWrapper, ManageBoxItemModelWrapper
from ..model_wrappers import ManifestItemModelWrapper, ManifestModelWrapper
from edc_lab.models.box_item import BoxItem


app_config = django_apps.get_app_config('edc_lab_dashboard')


class TestModelWrapper(TestCase):

    def setUp(self):
        self.box_type = BoxType.objects.create(
            name='9 x 9',
            across=9, down=9, total=81)
        self.box = Box.objects.create(
            box_identifier='12345678',
            box_type=self.box_type)
        self.box_item = BoxItem.objects.create(
            box=self.box, position=0)
        self.aliquot = Aliquot.objects.create(
            subject_identifier='ABCDEFG',
            count=1,
            is_primary=True,
            aliquot_type='Whole Blood',
            numeric_code='02',
            alpha_code='WB')

    def test_box_model_wrapper(self):
        wrapper_cls = BoxModelWrapper
        # usually this will come from app_config
        wrapper_cls.next_url_name = 'edc_lab:pack_listboard_url'
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
        # usually this will come from app_config
        wrapper_cls.next_url_name = 'edc_lab:manage_box_listboard_url'
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
        # usually this will come from app_config
        wrapper_cls.next_url_name = 'edc_lab:manage_manifest_listboard_url'
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
