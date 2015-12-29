from lis.specimen.lab_aliquot_list.models import BaseAliquotType

from ..managers import AliquotTypeManager


class AliquotType(BaseAliquotType):

    objects = AliquotTypeManager()

    class Meta:
        ordering = ["name"]
        app_label = 'lab_clinic_api'
