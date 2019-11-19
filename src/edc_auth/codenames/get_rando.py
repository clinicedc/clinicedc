from ..codename_tuples import get_rando_tuples


def get_rando():
    return [c[0] for c in get_rando_tuples()]
