import logging
from django.conf import settings
from lis.core.lab_grading.models import GradingList as LisGradingList, GradingListItem as LisGradingListItem
from ..models import GradingList, GradingListItem
from .base_import import BaseImport

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class ImportGrading(BaseImport):

    def get_or_create_list_item(self, test_code, list_obj, lis_list_item_obj, defaults):
        return GradingListItem.objects.get_or_create(
            grading_list=list_obj,
            grade=lis_list_item_obj.grade,
            test_code=test_code,
            uln=lis_list_item_obj.uln,
            lln=lis_list_item_obj.lln,
            age_low=lis_list_item_obj.age_low,
            age_low_unit=lis_list_item_obj.age_low_unit,
            defaults=defaults)

    def import_prep(self):
        self.lis_list_cls = LisGradingList
        self.lis_list_item_cls = LisGradingListItem
        self.lis_list_key_name = 'grading_list'
        self.list_name = settings.GRADING_LIST
        self.local_list_cls = GradingList
        self.local_list_item_cls = GradingListItem
        self.local_list_item_key_field_names = ['id', 'test_code', 'grading_list', 'grade', 'uln', 'lln', 'age_low', 'age_low_unit']
