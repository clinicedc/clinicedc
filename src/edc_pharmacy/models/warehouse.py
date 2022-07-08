from django.db import models
from django.db.models import PROTECT
from edc_model import models as edc_models
from edc_sites.models import SiteModelMixin


class Manager(models.Manager):

    use_in_migrations = True


class ModelMixin(SiteModelMixin, models.Model):

    name = models.CharField(max_length=25, unique=True)

    description = models.CharField(max_length=250)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta(SiteModelMixin.Meta):
        abstract = True


class Warehouse(ModelMixin, edc_models.BaseUuidModel):
    class Meta(ModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"


class Room(ModelMixin, edc_models.BaseUuidModel):

    warehouse = models.ForeignKey(Warehouse, on_delete=PROTECT)

    class Meta(ModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Room"
        verbose_name_plural = "Rooms"


class Shelf(ModelMixin, edc_models.BaseUuidModel):

    room = models.ForeignKey(Room, on_delete=PROTECT)

    class Meta(ModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Shelf"
        verbose_name_plural = "Shelves"


class Box(ModelMixin, edc_models.BaseUuidModel):

    shelf = models.ForeignKey(Shelf, on_delete=PROTECT)

    def __str__(self):
        return self.name

    class Meta(ModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Box"
        verbose_name_plural = "Boxes"
