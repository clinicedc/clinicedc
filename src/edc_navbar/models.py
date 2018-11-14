from django.db import models


class Navbar(models.Model):

    """Dummy model to create content_type to link with permissions.

    Permissions are added against this models content_type
    by site_navbars.update_permission_codenames.

    See also: edc_permissions.permissions_updater
    """

    pass
