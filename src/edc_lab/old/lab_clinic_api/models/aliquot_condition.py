from lis.specimen.lab_aliquot_list.models import BaseAliquotCondition
from lis.specimen.lab_aliquot_list.managers import AliquotConditionManager


class AliquotCondition(BaseAliquotCondition):

    objects = AliquotConditionManager()

    class Meta:
        app_label = 'lab_clinic_api'
