from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.mail.message import EmailMessage
from edc_base.utils import get_utcnow


def send_email(action_item=None):
    email_recipients = action_item.action_cls.email_recipients
    if not action_item.emailed and email_recipients:
        from_email = settings.EMAIL_CONTACTS.get('data_manager')
        body = [
            mark_safe(
                'Do not reply to this email\n\n'
                f'A report has been submitted for patient '
                f'{action_item.subject_identifier} '
                f'at site {action_item.site} which may require '
                f'your attention.\n\n'
                f'Title: {action_item.action_type.display_name}\n\n'
                f'You received this message because you are listed as a '
                f'member the Ambition Trial TMG\n\n'
                'Thanks.')
        ]
        email_message = EmailMessage(
            subject=(
                f'Ambition: {action_item.action_type.display_name} '
                f'for {action_item.subject_identifier}'),
            body='\n\n'.join(body),
            from_email=from_email,
            to=email_recipients)
        if settings.EMAIL_ENABLED:
            email_message.send()
            action_item.emailed = True
            action_item.emailed_datetime = get_utcnow()
            action_item.save()
