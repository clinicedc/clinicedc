from django.db import models


class EdcPermissionsManager(models.Manager):
    def get_by_natural_key(self, pk):
        return self.get(id=pk)


class EdcPermissionsModelMixin(models.Model):
    objects = EdcPermissionsManager()

    def __str__(self):
        return self._meta.app_label

    def natural_key(self):
        return (self.id,)

    class Meta:
        abstract = True
        verbose_name = "Edc Permissions"
        verbose_name_plural = "Edc Permissions"
