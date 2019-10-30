from django.conf import settings
from edc_model.models import BaseUuidModel


class Dashboard(BaseUuidModel):

    # see edc_auth for permissions attached to this model
    # create_edc_dashboard_permissions

    pass


if settings.APP_NAME == "edc_dashboard":
    from .tests import models  # noqa
