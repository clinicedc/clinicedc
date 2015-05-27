from django.core.exceptions import ImproperlyConfigured


class ScheduledModelMixin(object):

    def get_visit(self):
        """Returns the model field that points to the visit tracking model."""
        raise ImproperlyConfigured('Method must be overridden.')
