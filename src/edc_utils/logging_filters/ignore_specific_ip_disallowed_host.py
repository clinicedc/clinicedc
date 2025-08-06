from django.core.exceptions import DisallowedHost


class IgnoreSpecificIPDisallowedHost:
    def __init__(self, ip_to_ignore):
        self.ip_to_ignore = ip_to_ignore

    def filter(self, record):
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            if isinstance(exc_value, DisallowedHost):
                request = getattr(record, "request", None)
                if request and request.META.get("REMOTE_ADDR") == self.ip_to_ignore:
                    return False  # Suppress this log
        return True  # Allow all other logs
