from django.db import models
from django.db.models import PROTECT
from edc_model import models as edc_models
from edc_sites.models import SiteModelMixin

from .formulation import Formulation
from .list_models import Container


class Manager(models.Manager):

    use_in_migrations = True

    # def get_by_natural_key(self, container, count_per_container, *args):
    #     Medication.objects.get(*args)
    #     return self.get(name, strength, units, formulation)


class MedicationStock(SiteModelMixin, edc_models.BaseUuidModel):

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT)

    container = models.ForeignKey(Container, on_delete=PROTECT)

    count_per_container = models.DecimalField(max_digits=6, decimal_places=1)

    expiration_date = models.DateField(null=True, blank=True)

    lot_no = models.CharField(max_length=25, null=True, blank=True)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return (
            f"{self.formulation.description}. "
            f"{self.container} of "
            f"{self.count_per_container} {self.formulation.get_form_display()}"
        )

    # def natural_key(self):
    #     return (
    #         (self.count_per_container,)
    #         + self.container.natural_key()
    #         + self.formulation.natural_key()
    #     )

    class Meta(SiteModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Medication stock"
        verbose_name_plural = "Medication stock"
