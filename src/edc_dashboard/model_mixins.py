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
        slugs = [slugify(item) for item in self.get_slugs()]
        self.slug = '{}'.format('|'.join(slugs))
        return super().save(*args, **kwargs)

    def get_slugs(self):
        """Returns a list of field values as strings.

        Override.
        """
        return []

    class Meta:
        abstract = True
