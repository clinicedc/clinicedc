
class AlreadyRegistered(Exception):
    pass


class ReferenceCollection:

    def __init__(self, name=None):
        self._registry = {}
        self.name = name

    def __repr__(self):
        return f'{self.__class__.__name__}(\'{self.name}\')'

    def __iter__(self):
        for name, grp in self._registry.items():
            yield(name, grp)

    def register(self, grp=None):
        if grp.name in self._registry:
            raise AlreadyRegistered(f'Got {repr(grp)}')
        else:
            self._registry.update({grp.name: grp})

    def get(self, name):
        return self._registry.get(name)

    def update_grp(self, grp):
        self._registry.update({grp.name: grp})

    def as_data(self):
        data = {'normal': [], 'grading': []}
        for name, grp in self._registry.items():
            for normal_refs in grp.normal.values():
                for ref in normal_refs:
                    dct = ref.__dict__
                    dct.update(name=name)
                    dct = {k: v for k, v in dct.items() if k not in [
                        'evaluator', 'age_evaluator']}
                    data['normal'].append(dct)
        for name, grp in self._registry.items():
            for grade_refs in grp.grading.values():
                for ref in grade_refs:
                    dct = ref.__dict__
                    dct.update(name=name)
                    dct = {k: v for k, v in dct.items() if k not in [
                        'evaluator', 'age_evaluator']}
                    data['grading'].append(dct)
        return data
