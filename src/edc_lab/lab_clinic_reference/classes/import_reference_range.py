import logging
from django.conf import settings
from lis.specimen.lab_test_code.models import TestCodeReferenceList, TestCodeReferenceListItem
from ..models import ReferenceRangeList, ReferenceRangeListItem
from .base_import import BaseImport

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class ImportReferenceRange(BaseImport):

    def get_or_create_list_item(self, test_code, list_obj, lis_list_item_obj, defaults):
        return ReferenceRangeListItem.objects.get_or_create(
            reference_range_list=list_obj,
            test_code=test_code,
            uln=lis_list_item_obj.uln,
            lln=lis_list_item_obj.lln,
            age_low=lis_list_item_obj.age_low,
            age_low_unit=lis_list_item_obj.age_low_unit,
            defaults=defaults)

    def import_prep(self):
        self.lis_list_cls = TestCodeReferenceList
        self.lis_list_item_cls = TestCodeReferenceListItem
        self.lis_list_key_name = 'test_code_reference_list'
        self.list_name = settings.REFERENCE_RANGE_LIST
        self.local_list_cls = ReferenceRangeList
        self.local_list_item_cls = ReferenceRangeListItem
        self.local_list_item_key_field_names = ['id', 'test_code', 'test_code_reference_list', 'uln', 'lln', 'age_low', 'age_low_unit']
