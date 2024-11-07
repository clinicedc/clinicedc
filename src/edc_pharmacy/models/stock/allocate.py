# from django.db import models
# from edc_model.models import BaseUuidModel, HistoricalRecords
# from edc_utils import get_utcnow
# from sequences import get_next_value
#
# from ...exceptions import RepackRequestError
# from ..proxy_models import LabelSpecificationProxy
# from .container import Container
# from .stock import Stock
#
#
# class Manager(models.Manager):
#     use_in_migrations = True
#
#
# class Allocate(BaseUuidModel):
#
#     item_count = models.IntegerField(default=0)
#
#
