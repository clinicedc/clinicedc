# from django.conf import settings
# from django.core.exceptions import ImproperlyConfigured
# from edc.core.bhp_sms.classes import Sms
# from ..models import PendingIdentifier
# from ..models import SubjectIdentifier
# 
# 
# class SmsSubjectIdentifier(SubjectIdentifier):
# 
#     def get_post_identifier(self, identifier, **kwargs):
#         """Queues a request for an edc_identifier via SMS."""
#         app_name = settings.APP_NAME
#         pending_identifier = PendingIdentifier()
#         pending_identifier.pending_identifier = identifier
#         pending_identifier.app_name = app_name
#         sms = Sms()
#         sms_queue_id = sms.queue_message(pending_identifier.app_name, identifier)
#         if not sms_queue_id:
#             raise ImproperlyConfigured('Expected response from SMS module')
#         else:
#             pending_identifier.request_id = sms_queue_id
#             pending_identifier.save()
#         return identifier
