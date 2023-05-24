from edc_model.models import BaseUuidModel

from ..model_mixins import EdcPermissionsModelMixin


class EdcPermissions(EdcPermissionsModelMixin, BaseUuidModel):
    # see edc_auth for permissions attached to this model

    class Meta(EdcPermissionsModelMixin.Meta):
        pass
