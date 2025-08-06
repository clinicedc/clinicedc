from django.db import models


class ExportData(models.Model):
    """Dummy model for permissions"""

    class Meta:
        permissions = [("display_export_admin_action", "Display export action")]


class ImportData(models.Model):
    """Dummy model for permissions"""

    class Meta:
        permissions = [("display_import_admin_action", "Display import action")]
