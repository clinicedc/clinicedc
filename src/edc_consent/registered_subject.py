import six
from django import get_version

if get_version().startswith('1.6') and six.PY2:
    from edc.subject.registration.models import RegisteredSubject
else:
    from edc_registration.models import RegisteredSubject
