import logging
from django.db import models

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class ScheduleGroupManager(models.Manager):

    def get_by_natural_key(self, group_name):
        """Returns the natural key for serialization."""
        return self.get(group_name=group_name)
