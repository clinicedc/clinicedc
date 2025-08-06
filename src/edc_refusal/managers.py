from django.db import models

from edc_search.model_mixins import SearchSlugManager


class SubjectRefusalManager(SearchSlugManager, models.Manager):
    def get_by_natural_key(self, screening_identifier):
        return self.get(screening_identifier=screening_identifier)
