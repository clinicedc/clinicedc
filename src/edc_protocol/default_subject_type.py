from django.conf import settings

try:
    default_subject_type = settings.DEFAULT_SUBJECT_TYPE
except AttributeError:
    pass
if not default_subject_type:
    default_subject_type = 'subject'
