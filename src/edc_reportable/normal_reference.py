from .constants import LLN, ULN
from .value_reference import ValueReference


class NormalReferenceError(Exception):
    pass


class NormalReference(ValueReference):
    def __init__(self, name=None, lower=None, upper=None, **kwargs):
        string = f"{(lower or '')}{(upper or '')}"
        if ULN in string or LLN in string:
            raise NormalReferenceError(
                f"{LLN} and {ULN} are not relevant to a normal range. See {name}."
            )
        super().__init__(name=name, lower=lower, upper=upper, **kwargs)
