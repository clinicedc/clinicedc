from copy import deepcopy


class AlreadyRegistered(Exception):
    pass


class ReferenceCollection:

    def __init__(self):
        self._registry = {}

    def register(self, grp=None):
        if grp.name in self._registry:
            raise AlreadyRegistered(f'Got repr(grp)')
        else:
            self._registry.update({grp.name: grp})

    def get(self, name):
        return deepcopy(self._registry.get(name))
