from typing import Optional

from django.apps import apps as django_apps
from django.db import models
from edc_model.stubs import BaseUuidModelStub

from .notification import Notification


class ModelNotification(Notification):

    model: Optional[str] = None  # label_lower format

    email_body_template: str = (
        "\n\nDo not reply to this email\n\n"
        "{test_body_line}"
        "A report has been submitted for patient "
        "{instance.subject_identifier} "
        "at site {instance.site.name} which may require "
        "your attention.\n\n"
        "Title: {display_name}\n\n"
        "You received this message because you are subscribed to receive these "
        "notifications in your user profile.\n\n"
        "{test_body_line}"
        "Thanks."
    )
    email_subject_template: str = (
        "{test_subject_line}{protocol_name}: "
        "{display_name} "
        "for {instance.subject_identifier}"
    )
    sms_template: str = (
        '{test_line}{protocol_name}: Report "{display_name}" for '
        "patient {instance.subject_identifier} "
        "at site {instance.site.name} may require "
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

    def notify_on_condition(self, instance: BaseUuidModelStub = None, **kwargs) -> bool:
        """Override to notify is cls.model matches models instance name"""
        return instance._meta.label_lower == self.model  # type:ignore

    def get_template_options(self, instance=None, test_message=None, **kwargs) -> dict:
        opts = super().get_template_options(
            instance=instance, test_message=test_message, **kwargs
        )
        opts.update(message_reference=instance.id)
        return opts

    @property
    def test_template_options(self) -> dict:
        class Site:
            domain = "gaborone.example.com"
            name = "gaborone"
            id = 99

        class Meta:
            label_lower = self.model

        class DummyInstance:
            id = 99
            subject_identifier = "123456910"
            site = Site()
            _meta = Meta()

        instance = DummyInstance()
        return dict(instance=instance)
