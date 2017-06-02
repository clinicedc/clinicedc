from django.db import models

from .search_slug import SearchSlug


class SearchSlugManager(models.Manager):

    def update_search_slugs(self):
        for obj in self.all():
            obj.save_base(update_fields=['slug'])


class SearchSlugModelMixin(models.Model):

    search_slug_fields = []
    SEARCH_SLUG_SEP = '|'

    slug = models.CharField(
        max_length=250,
        null=True,
        editable=False,
        db_index=True,
        help_text='a field used for quick search')

    def save(self, *args, **kwargs):
        self.slug = SearchSlug(
            obj=self,
            fields=self.search_slug_fields,
            sep=self.SEARCH_SLUG_SEP).slug
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
