from django.db import models
from tqdm import tqdm

from .generate_slug import generate_slug


class SearchSlugManager(models.Manager):
    def update_search_slugs(self) -> None:
        qs = self.all()
        for obj in tqdm(qs, total=qs.count()):
            obj.slug = generate_slug(obj, obj.get_search_slug_fields()) or ""
            obj.save_base(update_fields=["slug"])


class SearchSlugModelMixin(models.Model):
    def get_search_slug_fields(self) -> tuple[str, ...]:
        return ()

    slug = models.CharField(
        max_length=250,
        default="",
        editable=False,
        db_index=True,
        help_text="Hold slug field values for quick search. Excludes encrypted fields",
    )

    def save(self, *args, **kwargs):
        self.slug = generate_slug(self, self.get_search_slug_fields()) or ""
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        indexes = (models.Index(fields=["slug"]),)
