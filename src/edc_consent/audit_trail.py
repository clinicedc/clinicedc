import six
from django import get_version

if get_version().startswith('1.6') and six.PY2:
    from edc.audit.audit_trail import AuditTrail
else:
    from simple_history.models import HistoricalRecords as AuditTrail
