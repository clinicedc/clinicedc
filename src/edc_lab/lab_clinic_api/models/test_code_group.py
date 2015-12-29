from lis.specimen.lab_test_code.models import BaseTestCodeGroup
from ..managers import TestCodeGroupManager


class TestCodeGroup(BaseTestCodeGroup):

    objects = TestCodeGroupManager()

    class Meta:
        app_label = 'lab_clinic_api'
        ordering = ['code', ]
