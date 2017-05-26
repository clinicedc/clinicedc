
class FormsCollectionError(Exception):
    pass


class FormsCollection:

    def __init__(self, *items, **kwargs):
        items = [] if not items or items == (None,) else list(items)
        try:
            items.sort(key=lambda x: x.show_order)
        except AttributeError as e:
            raise FormsCollectionError(e) from e
        self.items = tuple(items)
        seq = [item.show_order for item in self.items or []]
        if len(list(set(seq))) != len(seq):
            raise FormsCollectionError(
                f'{self.__class__.__name__} "show order" must be a '
                f'unique sequence. Got {seq}.')
