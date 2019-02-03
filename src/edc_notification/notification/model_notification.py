from django.apps import apps as django_apps

from .notification import Notification


class ModelNotification(Notification):

    model = None

    email_body_template = (
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
    email_subject_template = (
        "{test_subject_line}{protocol_name}: "
        "{display_name} "
        "for {instance.subject_identifier}"
    )
    sms_template = (
        '{test_line}{protocol_name}: Report "{display_name}" for '
        "patient {instance.subject_identifier} "
        "at site {instance.site.name} may require "
        "your attention. Login to review. (See your user profile to unsubscribe.)"
    )

    def __init__(self):
        super().__init__()
        if not self.display_name:
            self.display_name = django_apps.get_model(
                self.model
            )._meta.verbose_name.title()

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}:name='{self.name}', "
            f"display_name='{self.display_name}',"
            f"model='{self.model}'>"
        )

    def __str__(self):
        return f"{self.name}: {self.display_name} ({self.model})"

    def notify(self, force_notify=None, use_email=None, use_sms=None, **kwargs):
        """Overridden to only call `notify` if model matches.
        """
        notified = False
        instance = kwargs.get("instance")
        if instance._meta.label_lower == self.model:
            notified = super().notify(
                force_notify=force_notify,
                use_email=use_email,
                use_sms=use_sms,
                **kwargs,
            )
        return notified

    def get_template_options(self, instance=None, test_message=None, **kwargs):
        opts = super().get_template_options(
            instance=instance, test_message=test_message, **kwargs
        )
        opts.update(message_reference=instance.id)
        return opts

    @property
    def test_template_options(self):
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
