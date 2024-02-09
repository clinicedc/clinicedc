from __future__ import annotations

from django.db import models


class CharField2(models.CharField):
    def __init__(self, *args, metadata: str | dict | None = None, **kwargs):
        self.metadata = metadata
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.metadata is not None:
            kwargs["metadata"] = self.metadata
        return name, path, args, kwargs


class IntegerField2(models.IntegerField):
    def __init__(self, *args, metadata: str | dict | None = None, **kwargs):
        self.metadata = metadata
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.metadata is not None:
            kwargs["metadata"] = self.metadata
        return name, path, args, kwargs


class ManyToManyField2(models.ManyToManyField):
    def __init__(self, *args, metadata: str | dict | None = None, **kwargs):
        self.metadata = metadata
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.metadata is not None:
            kwargs["metadata"] = self.metadata
        return name, path, args, kwargs
