from django.db import models


class SearchSlugManager(models.Manager):

    def update_search_slugs(self):
        for obj in self.all():
            obj.update_search_slugs()
            obj.save_base(update_fields=['slug'])
