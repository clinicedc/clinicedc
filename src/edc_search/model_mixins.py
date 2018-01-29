from django.db import models

from .search_slug import SearchSlug


class SearchSlugDuplicateFields(Exception):
    pass


class SearchSlugUpdater:

    search_slug_cls = SearchSlug
    sep = '|'

    def __init__(self, fields, model_obj=None):
        if len(fields) > len(list(set(fields))):
            raise SearchSlugDuplicateFields(
                f'Duplicate search slug fields detected. Got {fields}. '
                f'See {repr(self)}')
        search_slug = self.search_slug_cls(
            obj=model_obj, fields=fields, sep=self.sep)
        self.warning = search_slug.warning
        self.slug = search_slug.slug


class SearchSlugManager(models.Manager):

    search_slug_updater_cls = SearchSlugUpdater
    search_slug_field_name = 'slug'

    def update_search_slugs(self):
        for obj in self.all():
            updater = self.search_slug_updater_cls(
                fields=obj.get_search_slug_fields(),
                model_obj=obj)
            setattr(obj, self.search_slug_field_name, updater.slug)
            obj.save_base(update_fields=[self.search_slug_field_name])


class SearchSlugModelMixin(models.Model):

    search_slug_warning = None
    search_slug_updater_cls = SearchSlugUpdater

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
        updater = self.search_slug_updater_cls(
            fields=self.get_search_slug_fields(), model_obj=self)
        self.search_slug_warning = updater.warning
        self.slug = updater.slug
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
