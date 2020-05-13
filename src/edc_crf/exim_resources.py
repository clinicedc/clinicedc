from import_export.resources import ModelResource

from .models import CrfStatus


class CrfStatusResource(ModelResource):
    class Meta:
        model = CrfStatus
