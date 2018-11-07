from django.apps import apps as django_apps

from .notification import Notification


class ModelNotification(Notification):

    model = None

    email_body_template = (
        '\n\nDo not reply to this email\n\n'
        '{test_body_line}'
        'A report has been submitted for patient '
        '{instance.subject_identifier} '
        'at site {instance.site.name} which may require '
        'your attention.\n\n'
        'Title: {display_name}\n\n'
        'You received this message because you are subscribed to receive these '
        'notifications in your user profile.\n\n'
        '{test_body_line}'
        'Thanks.')
    email_subject_template = (
        '{test_subject_line}{protocol_name}: '
        '{display_name} '
        'for {instance.subject_identifier}')
    sms_template = (
        '{test_line}{protocol_name}: Report "{display_name}" for '
        'patient {instance.subject_identifier} '
        'at site {instance.site.name} may require '
        'your attention. Login to review. (See your user profile to unsubscribe.)')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.display_name:
            self.display_name = django_apps.get_model(
                self.model)._meta.verbose_name.title()

    def post_notification_actions(self, instance=None, **kwargs):
        pass

    @property
    def test_template_options(self):
        class Site:
            domain = 'gaborone.example.com'
            name = 'gaborone'
            id = 99

        class DummyInstance:
            subject_identifier = '123456910'
            site = Site()

        instance = DummyInstance()
        return dict(instance=instance)
