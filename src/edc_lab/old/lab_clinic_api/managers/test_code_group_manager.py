from django.db import models


class TestCodeGroupManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)
