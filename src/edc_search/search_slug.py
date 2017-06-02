from django.utils.text import slugify


class SearchSlug:

    def __init__(self, obj=None, fields=None, sep=None):

        sep = sep or '|'
        values = []
        if fields:
            for field in fields:
                value = obj
                for f in field.split('.'):
                    value = getattr(value, f)
                values.append(value)
        slugs = [slugify(item or '') for item in values]
        self.slug = f'{sep.join(slugs)}'
