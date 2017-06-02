from django.db import models
from django.utils.text import slugify


class SearchSlugManager(models.Manager):

    def update_search_slugs(self):
        for obj in self.all():
            obj.update_search_slugs()
            obj.save_base(update_fields=['slug'])


class SearchSlugModelMixin(models.Model):

    SEARCH_SLUG_SEP = '|'
    search_slug_fields = []

    slug = models.CharField(
        max_length=250,
        null=True,
        editable=False,
        db_index=True,
        help_text='a field used for quick search')

    def save(self, *args, **kwargs):
        self.slug = self.get_search_slug()
        return super().save(*args, **kwargs)

    def get_search_slug_values(self):
        """Returns a list of field values.
        """
        values = []
        for field in self.search_slug_fields:
            value = self
            for f in field.split('.'):
                value = getattr(value, f)
            values.append(value)
        return values

    def get_search_slug(self):
        """Returns a string of slugified values joined
        by SEARCH_SLUG_SEP.
        """
        slugs = [slugify(item or '') for item in self.get_search_slug_values()]
        return f'{self.SEARCH_SLUG_SEP.join(slugs)}'

    class Meta:
        abstract = True
