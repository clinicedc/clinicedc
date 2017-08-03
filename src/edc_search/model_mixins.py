from django.db import models

from .search_slug import SearchSlug


class SearchSlugDuplicateFields(Exception):
    pass


class SearchSlugManager(models.Manager):

    def update_search_slugs(self):
        for obj in self.all():
            obj.save_base(update_fields=['slug'])


class SearchSlugModelMixin(models.Model):

    _search_slug_warning = None
    SEARCH_SLUG_SEP = '|'

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
        fields = self.get_search_slug_fields()
        if len(fields) > len(list(set(fields))):
            raise SearchSlugDuplicateFields(
                f'Duplicate search slug fields detected. Got {fields}. '
                f'See {repr(self)}')
        search_slug = SearchSlug(
            obj=self, fields=fields, sep=self.SEARCH_SLUG_SEP)
        self._search_slug_warning = search_slug.warning
        if self.slug:
            self.slug = f'{self.slug}|{search_slug.slug}'
        else:
            self.slug = search_slug.slug
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
