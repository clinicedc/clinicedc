import sys

from django.core.management.color import color_style
from django.utils.text import slugify

style = color_style()


class SearchSlug:
    def __init__(self, obj=None, fields=None, sep=None):
        self.warning = None
        self.slug = None
        sep = sep or "|"
        values = []
        if fields:
            for field in fields:
                value = obj
                for f in field.split("."):
                    value = getattr(value, f)
                values.append(value)
        slugs = [slugify(item or "") for item in values]
        slug = f"{sep.join(slugs)}"
        if len(slug) > 250:
            self.warning = f"Warning! Search slug string exceeds 250 chars. See {repr(obj)}\n"
            sys.stdout.write(style.WARNING(self.warning))
        self.slug = slug[:250]
