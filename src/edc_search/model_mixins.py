from django.db import models

from .search_slug import SearchSlug


class SearchSlugManager(models.Manager):

    def update_search_slugs(self):
        for obj in self.all():
            obj.save_base(update_fields=['slug'])


class SearchSlugModelMixin(models.Model):

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
        search_slug = SearchSlug(
            obj=self,
            fields=self.get_search_slug_fields(),
            sep=self.SEARCH_SLUG_SEP)
        if self.slug:
            self.slug = f'{self.slug}|{search_slug.slug}'
        else:
            self.slug = search_slug.slug
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
