# import sys
#
# from django.conf import settings
# from django.utils.safestring import mark_safe
# from django.core.mail.message import EmailMessage
# from edc_utils import get_utcnow
#
# NEW_REPORT = 'new_report'
# UPDATED_REPORT = 'updated_report'
#
# message_templates = {
#     NEW_REPORT: (
#         'Do not reply to this email\n\n'
#         '{test_message}'
#         'A report has been submitted for patient '
#         '{action_item.subject_identifier} '
#         'at site {action_item.site} which may require '
#         'your attention.\n\n'
#         'Title: {action_item.action_type.display_name}\n\n'
#         'You received this message because you are listed as a '
#         'member the Ambition Trial TMG\n\n'
#         '{test_message}'
#         'Thanks.'),
#     UPDATED_REPORT: (
#         'Do not reply to this email\n\n'
#         '{test_message}'
#         'A report has been updated for patient '
#         '{action_item.subject_identifier} '
#         'at site {action_item.site} which may require '
#         'your attention.\n\n'
#         'Title: {action_item.action_type.display_name}\n\n'
#         'Reason: {reason}\n\n'
#         'You received this message because you are listed as a '
#         'member the Ambition Trial TMG\n\n'
#         '{test_message}'
#         'Thanks.')
# }
#
#
# def send_email(action_item=None, reason=None, template_name=None,
#                force_send=None, using=None):
#     #     if template_name:
#     #         print('send_email', f'action_item={action_item}',
#     #               f'reason={reason}', f'template_name={template_name}')
#     #     else:
#     #         print('send_email', f'action_item={action_item}')
#     return None
#
#     if 'migrate' not in sys.argv:
#         template_name = template_name or 'new_report'
#         updated = '*UPDATE* ' if template_name == 'updated_report' else ''
#         email_recipients = action_item.action_cls.email_recipients
#         try:
#             email_enabled = settings.EMAIL_ENABLED
#         except AttributeError:
#             email_enabled = False
#         if email_enabled and email_recipients and (
#                 not action_item.emailed or force_send):
#             test_message = ''
#             test_subject = ''
#             try:
#                 live_system = settings.LIVE_SYSTEM
#             except AttributeError:
#                 live_system = False
#             if not live_system:
#                 test_message = 'THIS IS A TEST MESSAGE. NO ACTION IS REQUIRED\n\n'
#                 test_subject = 'TEST/UAT -- '
#             from_email = settings.EMAIL_CONTACTS.get('data_manager')
#             message = message_templates[template_name].format(
#                 test_message=test_message,
#                 action_item=action_item,
#                 reason=reason)
#             body = [mark_safe(message)]
#             email_message = EmailMessage(
#                 subject=(
#                     f'{test_subject}{updated}Ambition: '
#                     f'{action_item.action_type.display_name} '
#                     f'for {action_item.subject_identifier}'),
#                 body='\n\n'.join(body),
#                 from_email=from_email,
#                 to=email_recipients)
#             email_message.send()
#             action_item.emailed = True
#             action_item.emailed_datetime = get_utcnow()
#             action_item.save(using=using)
