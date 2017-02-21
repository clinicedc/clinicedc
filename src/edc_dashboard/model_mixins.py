from django.db import models
from django.utils.text import slugify


class SearchSlugModelMixin(models.Model):

    slug = models.CharField(
        max_length=250,
        null=True,
        editable=False,
        db_index=True,
        help_text='a field used for quick search')

    def save(self, *args, **kwargs):
        self.update_search_slugs()
        return super().save(*args, **kwargs)

    def get_slugs(self):
        """Returns a list of field values as strings.

        Override.
        """
        return []

    def update_search_slugs(self):
        slugs = [slugify(item) for item in self.get_slugs()]
        self.slug = '{}'.format('|'.join(slugs))

    class Meta:
        abstract = True


class SearchSlugManager(models.Manager):

    def update_search_slugs(self):
        for obj in self.all():
            obj.update_search_slugs()
            obj.save_base(update_fields=['slug'])
