from django.apps import apps as django_apps

from edc_model.stubs import BaseUuidHistoryModelStub

from ..constants import CREATE, DELETE, UPDATE
from .notification import Notification


class ModelNotification(Notification):
    """Generate a notification based on a model condition.

    Model must use the historical_model manager.

    The default condition is notify upon model creation
    modification or deletion.
    """

    model: str | None = None  # label_lower format

    model_operations: tuple[str] = (CREATE, UPDATE, DELETE)

    create_fields: tuple[str] = ("created",)
    update_fields: tuple[str] = ("modified",)

    email_body_template: str = (
        "\n\nDo not reply to this email\n\n"
        "{test_body_line}"
        "A report has been submitted for patient "
        "{subject_identifier} "
        "at site {site_name} which may require "
        "your attention.\n\n"
        "Title: {display_name}\n\n"
        "You received this message because you are subscribed to receive these "
        "notifications in your user profile.\n\n"
        "{test_body_line}"
        "Thanks."
    )
    email_subject_template: str = (
        "{test_subject_line}{protocol_name}: {model_operation} "
        "{display_name} for {subject_identifier}"
    )
    sms_template: str = (
        "{test_line}{protocol_name}: {model_operation}Report '{display_name}' for "
        "patient {subject_identifier} "
        "at site '{site_name}' may require "
        "your attention. Login to review. (See your user profile to unsubscribe.)"
    )

    def __init__(self) -> None:
        super().__init__()
        if not self.display_name:
            self.display_name = django_apps.get_model(self.model)._meta.verbose_name.title()

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}:name='{self.name}', "
            f"display_name='{self.display_name}',"
            f"model='{self.model}'>"
        )

    def __str__(self) -> str:
        return f"{self.name}: {self.display_name} ({self.model})"

    def notify_on_condition(self, instance: BaseUuidHistoryModelStub = None, **kwargs) -> bool:
        """Returns True if the condition in one of the C(r)UD methods is met."""
        if instance._meta.label_lower == self.model:
            return (
                self.is_create(instance, **kwargs)
                or self.is_update(instance, **kwargs)
                or self.is_delete(instance, **kwargs)
            )
        return False

    def is_create(self, instance, **kwargs):
        """Returns True if we are watching for a CREATE model operation, this is a
        CREATE model operation, and the custom create condition is met.
        """
        history_type = self.get_history_type(instance)
        return (
            history_type in self.model_operations
            and history_type == CREATE
            and self.notify_on_create_condition(instance, **kwargs)
        )

    def notify_on_create_condition(self, instance, **kwargs):
        """Returns a dictionary or None of {field: value, ...}
        for field values in `create_fields`.
        """
        created_fields = {}
        if self.create_fields:
            created = {}
            for field in self.create_fields:
                value = getattr(instance, field)
                created.update({field: value})
            for field, value in created.items():
                if self.field_value_condition_on_create(field, value):
                    created_fields.update({field: value})
        return created_fields or None

    def field_value_condition_on_create(self, field, current_value) -> bool:
        """Returns True or False.

        Override for a more complex evaluation.
        """
        return True

    def is_update(self, instance, **kwargs):
        """Returns True if we are watching for a UPDATE model operation, this is a
        UPDATE model operation, and the custom create condition is met.
        """
        history_type = self.get_history_type(instance)
        return (
            history_type in self.model_operations
            and history_type == UPDATE
            and self.notify_on_update_condition(instance, **kwargs)
        )

    def notify_on_update_condition(self, instance, **kwargs):
        """Returns a dictionary or None of {field: [previous_value, current_value], ...}
        for field values in `update_fields` that have changed.
        """
        changed_fields = {}
        if self.update_fields and instance.history.all().count() > 1:
            changes = {}
            for field in self.update_fields:
                values = [getattr(obj, field) for obj in self.get_history(instance)]
                changes.update({field: values[:2]})
            for field, values in changes.items():
                if self.field_value_condition_on_update(field, values[1], values[0]):
                    changed_fields.update({field: values})
        return changed_fields or None

    def field_value_condition_on_update(self, field, previous_value, current_value) -> bool:
        """Returns True if the value has changed.

        Override for a more complex evaluation.
        """
        return previous_value != current_value

    def is_delete(self, instance, **kwargs):
        history_type = instance.history.all().order_by("-history_date")[0].history_type
        return history_type in self.model_operations and history_type == DELETE

    @staticmethod
    def get_history(instance):
        """Returns the history queryset in desc order by `history_date`"""
        return instance.history.all().order_by("-history_date")

    @staticmethod
    def get_history_type(instance):
        """Returns the `history_type` of the most recent historical instance"""
        return instance.history.all().order_by("-history_date")[0].history_type

    def get_model_operation_as_text(self, instance=None, test_message=None, **kwargs):
        opts = {
            CREATE: "",
            UPDATE: "UPDATE* ",
            DELETE: "DELETED* ",
        }
        if not instance and test_message:
            return ""
        return f"{opts.get(self.get_history_type(instance))}"

    def get_template_options(self, instance=None, test_message=None, **kwargs) -> dict:
        opts = super().get_template_options(
            instance=instance, test_message=test_message, **kwargs
        )
        opts.update(
            message_reference=getattr(
                instance,
                "id",
                "test-message-id",
            ),
            model_operation=self.get_model_operation_as_text(
                instance=instance, test_message=test_message, **kwargs
            ),
        )

        return opts
