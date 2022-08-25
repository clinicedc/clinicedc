from edc_auth.model_mixins import EdcPermissionsModelMixin
from edc_model.models import BaseUuidModel


class EdcPermissions(EdcPermissionsModelMixin, BaseUuidModel):

    # see edc_auth for permissions attached to this model

    class Meta(EdcPermissionsModelMixin.Meta):
        pass
