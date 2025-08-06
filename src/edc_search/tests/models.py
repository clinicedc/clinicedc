__all__ = ["TestModel", "TestModelExtra"]

from django.db import models

from ..model_mixins import SearchSlugManager, SearchSlugModelMixin


class Dummy:
    attr = "dummy_attr"

    def __str__(self):
        return "Dummy"


class TestModelMixin(SearchSlugModelMixin, models.Model):
    f1 = models.CharField(max_length=25, null=True)

    f2 = models.DateTimeField(null=True)

    f3 = models.IntegerField(null=True)

    objects = SearchSlugManager()

    @property
    def attr(self):
        return "attr"

    @property
    def dummy(self):
        return Dummy()

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.extend(["f1", "f2", "f3", "attr", "dummy", "dummy.attr"])
        return fields

    class Meta:
        abstract = True


class TestModel(TestModelMixin, models.Model):
    pass


class TestModelExtra(TestModelMixin, models.Model):
    f4 = models.CharField(max_length=25, null=True)

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.append("f4")
        return fields


class TestModelDuplicate(TestModelMixin, models.Model):
    f4 = models.CharField(max_length=25, null=True)

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.extend(["f1", "f4"])
        return fields
