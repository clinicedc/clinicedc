from django.db import models

from .search_slug import SearchSlug


class SearchSlugDuplicateFields(Exception):
    pass


class SearchSlugUpdater:
    def __init__(self, fields, model_obj=None):
        if len(fields) > len(list(set(fields))):
            raise SearchSlugDuplicateFields(
                f'Duplicate search slug fields detected. Got {fields}. '
                f'See {repr(self)}')
        search_slug = SearchSlug(
            obj=model_obj, fields=fields, sep='|')
        self.warning = search_slug.warning
        self.slug = search_slug.slug


class SearchSlugManager(models.Manager):

    def update_search_slugs(self):
        for obj in self.all():
            updater = SearchSlugUpdater(
                fields=obj.get_search_slug_fields(),
                model_obj=obj)
            obj.slug = updater.slug
            obj.save_base(update_fields=['slug'])


class SearchSlugModelMixin(models.Model):

    _search_slug_warning = None

    def get_search_slug_fields(self):
        return []

    slug = models.CharField(
        max_length=250,
        default='',
        null=True,
        editable=False,
        db_index=True,
        help_text='a field used for quick search')

    def save(self, *args, **kwargs):
        updater = SearchSlugUpdater(
            fields=self.get_search_slug_fields(), model_obj=self)
        self._search_slug_warning = updater.warning
        self.slug = updater.slug
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
