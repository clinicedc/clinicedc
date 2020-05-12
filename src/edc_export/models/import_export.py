from django.db import models


class ExportData(models.Model):
    """Dummy model for permissions"""

    class Meta:
        permissions = [("show_export_admin_action", "Show export action")]


class ImportData(models.Model):
    """Dummy model for permissions"""

    class Meta:
        permissions = [("show_import_admin_action", "Show import action")]
