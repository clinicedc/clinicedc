from django.db import models

from .model_exporter import ObjectHistoryCreator


class ExportHistoryManager(models.Manager):
    obj_creator = ObjectHistoryCreator()

    def serialize_to_exported_object_history(
        self, instance, change_type, using, force_export=False
    ):
        """Serialize this instance to the export transaction model if ready.

        Be sure to inspect model property ready_to_export_transaction.
        ready_to_export_transaction can return True or False. If False,
        the tx will not be exported.

        if model method :func:`ready_to_export_transaction` has not been defined,
        export will proceed.

        .. note:: If change_type == 'D', entire tx is still sent."""
        try:
            ready_to_export_transaction = force_export or instance.ready_to_export_transaction
        except AttributeError as attribute_error:
            if str(attribute_error).endswith("has no attribute 'ready_to_export_transaction'"):
                ready_to_export_transaction = True
            else:
                raise
        if ready_to_export_transaction:
            self.obj_creator.create(model_obj=instance, change_type=change_type, using=using)
