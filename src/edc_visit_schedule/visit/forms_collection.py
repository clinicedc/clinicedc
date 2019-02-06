from django.conf import settings


class FormsCollectionError(Exception):
    pass


class FormsCollection:
    def __init__(self, *forms, name=None, **kwargs):
        self._forms = None
        self.name = name
        forms = [] if not forms or forms == (None,) else list(forms)

        # exclude any flagged for a site that is not the current
        forms = [f for f in forms if not f.site_ids or settings.SITE_ID in f.site_ids]

        # sort on show order
        try:
            forms.sort(key=lambda x: x.show_order)
        except AttributeError as e:
            raise FormsCollectionError(e) from e

        # check sequence
        seq = [item.show_order for item in forms or []]
        if len(list(set(seq))) != len(seq):
            raise FormsCollectionError(
                f'{self.__class__.__name__} "show order" must be a '
                f"unique sequence. Got {seq}."
            )

        # convert to tuple
        self._forms = tuple(forms)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def __iter__(self):
        return iter(self._forms)

    @property
    def forms(self):
        return self._forms
