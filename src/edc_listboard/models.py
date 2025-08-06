from django.conf import settings

from edc_model.models import BaseUuidModel


class Listboard(BaseUuidModel):
    # see edc_auth for permissions attached to this model
    # create_edc_listboard_permissions

    pass


if settings.APP_NAME == "edc_listboard":
    from .tests import models  # noqa
