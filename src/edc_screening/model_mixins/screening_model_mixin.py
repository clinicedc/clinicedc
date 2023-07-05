from django.db import models
from edc_model.models import HistoricalRecords
from edc_search.model_mixins import SearchSlugManager
from edc_sites.model_mixins import CurrentSiteManager

from ..screening_identifier import ScreeningIdentifier
from .screening_fields_model_mixin import ScreeningFieldsModeMixin
from .screening_identifier_model_mixin import ScreeningIdentifierModelMixin
from .screening_methods_model_mixin import ScreeningMethodsModeMixin


class ScreeningManager(SearchSlugManager, models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, screening_identifier):
        return self.get(screening_identifier=screening_identifier)


class ScreeningModelMixin(
    ScreeningMethodsModeMixin,
    ScreeningIdentifierModelMixin,
    ScreeningFieldsModeMixin,
    models.Model,
):

    """You may wish to also include the `EligibilityModelMixin`
    in your declaration."""

    identifier_cls = ScreeningIdentifier

    # add `site` to your concrete model if asking for site confirmation
    # and on the screening form to make the field editable.
    # site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True, related_name="+")

    objects = ScreeningManager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
