from .models import NormalData
from .value_reference import ValueReference


class NormalReferenceError(Exception):
    pass


class NormalReference(ValueReference):
    def __init__(self, name=None):
        normal_data = NormalData.objects.filter(label=name)
        super().__init__(name=name, normal_data=normal_data)
